from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from products.models import Products
from django.urls import reverse_lazy, reverse
from django import forms
from django.core.exceptions import ValidationError
from .models import Sale
from django.utils.dateparse import parse_date
from django.db.models import Q, F, Sum, DecimalField, ExpressionWrapper
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from django.db import transaction
from django.utils.timezone import now


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'customer_name', 'discount', 'tax']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        if product and quantity:
            if quantity > product.quantity:
                raise ValidationError('الكمية المطلوبة أكبر من الكمية المتاحة في المخزون')
        return cleaned_data


class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_form.html'
    success_url = reverse_lazy('sale-list')

    def form_valid(self, form):
        with transaction.atomic():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            if product.quantity >= quantity:
                product.quantity -= quantity
                product.save()
                return super().form_valid(form)
            else:
                form.add_error('quantity', 'الكمية المطلوبة أكبر من الكمية المتاحة في المخزون.')
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse('sale-invoice', kwargs={'pk': self.object.pk})


def reshape_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


class SaleListView(ListView):
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                queryset = queryset.filter(sale_date__date__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                queryset = queryset.filter(sale_date__date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        total = queryset.aggregate(
            total_sales=Sum(
                ExpressionWrapper(
                    F('quantity') * F('product__price'),
                    output_field=DecimalField()
                )
            )
        )
        context['total_sales'] = total['total_sales'] or 0

        today = now().date()
        daily_sales_qs = Sale.objects.filter(sale_date__date=today)
        daily_total = daily_sales_qs.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('product__price'),
                    output_field=DecimalField()
                )
            )
        )['total'] or 0
        context['daily_sales'] = daily_total

        current_month = now().month
        current_year = now().year
        monthly_sales_qs = Sale.objects.filter(sale_date__year=current_year, sale_date__month=current_month)
        monthly_total = monthly_sales_qs.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity') * F('product__price'),
                    output_field=DecimalField()
                )
            )
        )['total'] or 0
        context['monthly_sales'] = monthly_total

        # أفضل 5 منتجات مبيعًا
        top_5_selling = (
            Sale.objects
            .values('product__id', 'product__name')
            .annotate(total_quantity_sold=Sum('quantity'))
            .order_by('-total_quantity_sold')[:5]
        )
        context['top_selling'] = top_5_selling

        return context


class SaleInvoiceView(DetailView):
    model = Sale
    template_name = 'sales/sale_invoice.html'
    context_object_name = 'sale'

    def get(self, request, *args, **kwargs):
        sale = self.get_object()

        if request.GET.get("format") == "pdf":
            product = sale.product
            quantity = sale.quantity

            subtotal = product.price * quantity
            discount = sale.discount or 0
            tax_percentage = sale.tax or 0
            after_discount = subtotal - discount
            tax_value = (after_discount * tax_percentage) / 100
            total_price = after_discount + tax_value
            sale_date = sale.sale_date

            width, height = letter
            font_path = 'E:/project/inventory_system/fonts/Amiri-Regular.ttf'
            logo_path = 'E:/project/inventory_system/media/image/logo.jpg'

            pdfmetrics.registerFont(TTFont('Amiri', font_path))

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{sale.id}.pdf"'

            p = canvas.Canvas(response, pagesize=letter)
            p.setFont("Amiri", 14)

            # إضافة اللوجو
            try:
                p.drawImage(logo_path, 40, height - 90, width=80, height=80, preserveAspectRatio=True)
            except Exception as e:
                print("Logo load error:", e)

            # بيانات الشركة
            p.setFont("Amiri", 12)
            p.drawRightString(550, height - 40, reshape_arabic_text("Apple phone"))
            p.drawRightString(550, height - 60, reshape_arabic_text("العنوان : ليسا الجمالية عزبة رفاعى"))
            p.drawRightString(550, height - 80, reshape_arabic_text("رقم الهاتف : 01002215373"))
            p.drawRightString(550, height - 100, reshape_arabic_text("إدراة الأستاذ : محمد حماده نور الدين"))

            y = height - 130
            p.line(40, y, 570, y)
            y -= 40

            # رأس الفاتورة
            p.setFont("Amiri", 14)
            x_right = 550
            p.drawRightString(x_right, y, reshape_arabic_text(f"فاتورة بيع رقم: {sale.id}"))
            y -= 25
            p.drawRightString(x_right, y, reshape_arabic_text(f"تاريخ البيع: {sale_date.strftime('%d-%m-%Y')}"))
            y -= 35

            style = ParagraphStyle(
                name='ArabicStyle',
                fontName='Amiri',
                fontSize=14,
                leading=20,
                alignment=TA_RIGHT,
                spaceAfter=10,
            )

            # بيانات الجدول كصفوف منفصلة بشكل أوضح
            data = [
                [Paragraph(reshape_arabic_text("اسم المنتج"), style),
                 Paragraph(reshape_arabic_text("الكمية"), style),
                 Paragraph(reshape_arabic_text("السعر"), style),
                 Paragraph(reshape_arabic_text("الإجمالي"), style)],
                [Paragraph(reshape_arabic_text(product.name), style),
                 Paragraph(reshape_arabic_text(str(quantity)), style),
                 Paragraph(reshape_arabic_text(f"{product.price} جنيه"), style),
                 Paragraph(reshape_arabic_text(f"{subtotal} جنيه"), style)],
                ['', '', Paragraph(reshape_arabic_text("الخصم"), style), Paragraph(reshape_arabic_text(f"{discount} جنيه"), style)],
                ['', '', Paragraph(reshape_arabic_text("الضريبة المضافة (%)"), style), Paragraph(reshape_arabic_text(f"{tax_percentage}%"), style)],
                ['', '', Paragraph(reshape_arabic_text("قيمة الضريبة"), style), Paragraph(reshape_arabic_text(f"{tax_value:.2f} جنيه"), style)],
                ['', '', Paragraph(reshape_arabic_text("السعر النهائي"), style), Paragraph(reshape_arabic_text(f"{total_price:.2f} جنيه"), style)],
            ]

            col_widths = [160, 80, 150, 150]
            table = Table(data, colWidths=col_widths, hAlign='RIGHT')

            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('GRID', (0, 0), (-1, 1), 1, colors.black),
                ('SPAN', (0, 2), (1, 2)),  # دمج خليتين خاص بالخصم لتنسيق أفضل
                ('SPAN', (0, 3), (1, 3)),  # دمج خليتين خاص بالضريبة المضافة
                ('SPAN', (0, 4), (1, 4)),  # دمج خليتين خاص بقيمة الضريبة
                ('SPAN', (0, 5), (1, 5)),  # دمج خليتين خاص بالسعر النهائي
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            table.wrapOn(p, width, height)
            table.drawOn(p, 40, y - 150)

            p.drawRightString(550, y - 180, reshape_arabic_text("شكراً لتعاملكم معنا"))

            p.showPage()
            p.save()
            return response
        else:
            return super().get(request, *args, **kwargs)
