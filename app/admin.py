from django.contrib import admin
from .models import Coupon, Product, Category,Profile,Cart,Wishlist,CustomUser,Order,OrderItem,SiteProfile,background_image_aat_index_page,booktable
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph ,Spacer
from reportlab.lib import colors
from django.conf import settings
import os
from django.utils import timezone
from reportlab.lib.styles import getSampleStyleSheet



def generate_invoice(order):
    invoices_dir = os.path.join(settings.MEDIA_ROOT, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")

    pdf_file = os.path.join(invoices_dir, f"order_{order.email}_{timestamp}.pdf")

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)

    elements = []

    styles= getSampleStyleSheet()

    elements.append(Paragraph(f"Invoice for Order {order.id}", styles['Title']))
    elements.append(Spacer(1, 20))  

    elements.append(Paragraph(f"Customer: {order.first_name} {order.last_name}", styles['Normal']))
    elements.append(Paragraph(f"Email: {order.email}", styles['Normal']))
    elements.append(Paragraph(f"Address: {order.address}", styles['Normal']))
    elements.append(Paragraph(f"City: {order.city}", styles['Normal']))
    elements.append(Paragraph(f"Country: {order.country}", styles['Normal']))
    elements.append(Paragraph(f"Zip Code: {order.zip_code}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {order.phone}", styles['Normal']))
    elements.append(Spacer(1, 30))

    data = [['Product', 'Quantity', 'Unit Price', 'Total']]

    for item in order.items.all():
        total = item.price * item.quantity   
        data.append([
            item.product.name,
            item.quantity,
            f"RS{item.price:.2f}",
            f"RS{total:.2f}"
        ])

    data.append(['', '', 'Grand Total', f"RS{order.total_amount:.2f}"])

    table = Table(data, colWidths=[200, 80, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("Thank you for your purchase!", styles['Normal']))
    doc.build(elements)

    return pdf_file


def generate_invoice_action(modeladmin, request, queryset):
    for order in queryset:
        generate_invoice(order)

    modeladmin.message_user(request, f"Invoices generated successfully for {queryset.count()} orders.")


generate_invoice_action.short_description = "Generate Invoice for selected orders"


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status']
    list_display_links = ['id', 'user']
    search_fields = ['user__username', 'id']
    actions = [generate_invoice_action]


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'price', 'category','stock_qty','company','site','is_new','has_discount','discount_percent','discount_start_date','discount_end_date']
    list_display_links=['id','name']
    search_fields = ['id','name']

admin.site.register(background_image_aat_index_page)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(CustomUser)
admin.site.register(Coupon)

class profileAdmin(admin.ModelAdmin):
    list_display = ['id','user',]
    list_display_links = ['user']
    search_fields = ['user__username']

admin.site.register(Profile, profileAdmin)

admin.site.register(SiteProfile)
admin.site.register(booktable)


# Register your models here.
