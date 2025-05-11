from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from products.models import Products
from django.urls import reverse_lazy ,reverse
from django import forms
from django.core.exceptions import ValidationError
from .models import Sale
from django.utils.dateparse import parse_date
from django.db.models import Q, F, Sum, DecimalField, ExpressionWrapper
from reportlab.lib.pagesizes import letter
from reportlab.lib import fonts , colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.platypus import Table, TableStyle ,Paragraph
from PIL import Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from django.db import transaction





class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity','customer_name','discount','tax']
        
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
        # قلل الكمية من المنتج بعد الحفظ
        with transaction.atomic():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
        # التحقق من أن المنتج يحتوي على كمية كافية
            if product.quantity >= quantity:
                product.quantity -= quantity
                product.save()
            # تقليل الكمية من المنتج في المخزون
                return super().form_valid(form)
            else:
                form.add_error('quantity', 'الكمية المطلوبة أكبر من الكمية المتاحة في المخزون.')
                return self.form_invalid(form)
    def get_success_url(self):
        return reverse('sale-invoice',kwargs={'pk':self.object.pk})

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
                queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                queryset = queryset.filter(sale_date__lte=end_date)
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
        return context
def reshape_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# إنشاء دالة لعرض الفاتورة PDF باستخدام CBV
class SaleInvoiceView(DetailView):
    model = Sale
    template_name = 'sales/sale_invoice.html'
    context_object_name = 'sale'

    

    def get(self, request, *args, **kwargs):
        sale = self.get_object()

        if request.GET.get("format") == "pdf":
            product = sale.product
            quantity = sale.quantity
            # السعر الأساسي
            subtotal = product.price * quantity

# الخصم بالجنيه
            discount = sale.discount or 0

# الضريبة بالنسبة المئوية
            tax_percentage = sale.tax or 0

# بعد الخصم
            after_discount = subtotal - discount

# قيمة الضريبة
            tax_value = (after_discount * tax_percentage) / 100

# السعر النهائي
            total_price = after_discount + tax_value
            sale_date = sale.sale_date

            width, height = letter
            font_path = 'E:/project/inventory_system/fonts/Amiri-Regular.ttf'
            logo_path = 'E:/project/inventory_system/media/image/logo.jpg'

            # تسجيل الخط العربي
            pdfmetrics.registerFont(TTFont('Amiri', font_path))

            # إعداد الاستجابة
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{sale.id}.pdf"'

            p = canvas.Canvas(response, pagesize=letter)
            p.setFont("Amiri", 14)

            # إضافة اللوجو
            try:
                p.drawImage(logo_path, 40, height - 100, width=80, height=80, preserveAspectRatio=True)
            except Exception as e:
                print("Logo load error:", e)

            # بيانات الشركة
            p.setFont("Amiri", 12)
            p.drawRightString(550, height - 50, reshape_arabic_text("شركة فرست لتجارة المواد الغذائية"))
            p.drawRightString(550, height - 70, reshape_arabic_text("العنوان : ليسا الجمالية عزبة رفاعى"))
            p.drawRightString(550, height - 90, reshape_arabic_text("رقم الهاتف : 01096549629"))

            y = height - 130
            p.line(40, y, 570, y)
            y -= 40

            # رأس الفاتورة
            p.setFont("Amiri", 14)
            x_right = 550
            p.drawRightString(x_right, y, reshape_arabic_text(f"فاتورة بيع رقم: {sale.id}")); y -= 25
            p.drawRightString(x_right, y, reshape_arabic_text(f"تاريخ البيع: {sale_date.strftime('%d-%m-%Y')}")); y -= 35

            # إعداد ستايل الفقرات للنصوص داخل الجدول
            style = ParagraphStyle(
                name='ArabicStyle',
                fontName='Amiri',
                fontSize=14,
                leading=18,
                alignment=TA_RIGHT,
            )

            # جدول الفاتورة باستخدام Paragraph لضبط النص داخل الخلايا
            table_data = [
                [Paragraph(reshape_arabic_text("اسم المنتج"), style),
                 Paragraph(reshape_arabic_text("الكمية"), style),
                 Paragraph(reshape_arabic_text("السعر"), style),
                 Paragraph(reshape_arabic_text("الإجمالي"), style),
                 Paragraph(reshape_arabic_text("الخصم :"),style),
                 Paragraph(reshape_arabic_text("الضريبة المضافة :"),style),
                 Paragraph(reshape_arabic_text("السعر النهائى :"),style),
                 
                 ],

                [Paragraph(reshape_arabic_text(product.name), style),
                 Paragraph(reshape_arabic_text(str(quantity)), style),
                 Paragraph(reshape_arabic_text(f"{product.price} جنيه"), style),
                 Paragraph(reshape_arabic_text(f"{total_price} جنيه"), style),
                 Paragraph(reshape_arabic_text(f"{subtotal} جنية"),style),
                 Paragraph(reshape_arabic_text(f"{discount}جنية"),style),
                 Paragraph(reshape_arabic_text(f"{tax_value:.2f} جنية"),style),
                 Paragraph(reshape_arabic_text(f"{total_price:.2f} جنية"),style)
                 ],
            ]    
                 
                
                
            

            table = Table(table_data, colWidths=[160, 100, 120, 120], rowHeights=[30, 30])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            # تحديد مكان الجدول
            table.wrapOn(p, width, height)
            table.drawOn(p, 40, y - 60)

            # شكر
            p.setFont("Amiri", 12)
            p.drawRightString(550, y - 120, reshape_arabic_text("شكرًا لاختياركم منتجاتنا!"))

            p.showPage()
            p.save()
            return response

        # عرض الفاتورة HTML
        context = {'sale': sale}
        return render(request, self.template_name, context)


