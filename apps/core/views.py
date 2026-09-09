from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, DecimalField, F, Sum
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView

from apps.catalogo.models import Producto
from apps.despacho.models import Pedido
from apps.inventario.models import Existencia, Movimiento
from apps.recepcion.models import OrdenRecepcion


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # El sistema tiene dos tableros: el Administrativo (superusuario, ve
        # todo) y el Operativo (Operario, solo lo necesario para su trabajo).
        context["es_administrador"] = self.request.user.is_superuser

        context["productos_activos"] = Producto.objects.filter(activo=True).count()
        context["ubicaciones_ocupadas"] = (
            Existencia.objects.filter(cantidad__gt=0).values("ubicacion").distinct().count()
        )
        context["recepciones_pendientes"] = OrdenRecepcion.objects.filter(
            estado__in=[OrdenRecepcion.Estado.PENDIENTE, OrdenRecepcion.Estado.PARCIAL]
        ).count()
        context["pedidos_pendientes"] = Pedido.objects.filter(
            estado__in=[Pedido.Estado.PENDIENTE, Pedido.Estado.EN_PICKING]
        ).count()

        # --- Gráfico: movimientos del kardex por tipo ---
        tipo_labels = dict(Movimiento.TipoMovimiento.choices)
        movimientos_qs = Movimiento.objects.values("tipo").annotate(total=Count("id")).order_by("tipo")
        context["mov_chart_labels"] = [tipo_labels.get(r["tipo"], r["tipo"]) for r in movimientos_qs]
        context["mov_chart_data"] = [r["total"] for r in movimientos_qs]
        context["mov_chart_total"] = sum(context["mov_chart_data"])

        # --- Actividad reciente (kardex): la ven ambos roles ---
        context["ultimos_movimientos"] = (
            Movimiento.objects.select_related("producto", "ubicacion_origen", "ubicacion_destino", "usuario")
            .order_by("-creado_en")[:8]
        )

        # --- El resto es analítica de catálogo/reportes: solo Administrador ---
        if context["es_administrador"]:
            abc_labels = dict(Producto.ClasificacionABC.choices)
            abc_qs = (
                Producto.objects.filter(activo=True)
                .values("clasificacion_abc")
                .annotate(total=Count("id"))
                .order_by("clasificacion_abc")
            )
            context["abc_chart_labels"] = [abc_labels.get(r["clasificacion_abc"], r["clasificacion_abc"]) for r in abc_qs]
            context["abc_chart_data"] = [r["total"] for r in abc_qs]
            context["abc_chart_total"] = sum(context["abc_chart_data"])

            context["productos_bajo_stock"] = (
                Producto.objects.filter(activo=True)
                .annotate(
                    stock_total=Coalesce(
                        Sum("existencias__cantidad"), Decimal("0"), output_field=DecimalField()
                    )
                )
                .filter(stock_total__lt=F("stock_minimo"))
                .order_by("stock_total")[:6]
            )

        return context
