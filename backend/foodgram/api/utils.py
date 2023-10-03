import io

from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from users.models import Subscription


def create_shopping_cart(ingredients_cart):
    """Функция формирования списка покупок."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        "attachment; filename='shopping_cart.pdf'"
    )
    pdfmetrics.registerFont(
        TTFont('Arial', 'arial.ttf', 'UTF-8')
    )
    buffer = io.BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setFont('Arial', 24)
    pdf_file.drawString(200, 800, 'Список покупок.')
    pdf_file.setFont('Arial', 14)
    from_bottom = 750
    for number, ingredient in enumerate(ingredients_cart, start=1):
        pdf_file.drawString(
            50,
            from_bottom,
            f"{number}. {ingredient['ingredient__name']}: "
            f"{ingredient['ingredient_value']} "
            f"{ingredient['ingredient__measurement_unit']}.",
        )
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            pdf_file.showPage()
            pdf_file.setFont('Arial', 14)
    pdf_file.showPage()
    pdf_file.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def create_object(request, pk, serializer_in, serializer_out, model):
    user = request.user.id
    obj = get_object_or_404(model, id=pk)

    data_recipe = {'user': user, 'recipe': obj.id}
    data_subscribe = {'user': user, 'author': obj.id}

    if model is Recipe:
        serializer = serializer_in(data=data_recipe)
    else:
        serializer = serializer_in(data=data_subscribe)

    serializer.is_valid(raise_exception=True)
    serializer.save()
    serializer_to_response = serializer_out(obj, context={'request': request})
    return serializer_to_response


def delete_object(request, pk, model_object, model_for_delete_object):
    user = request.user

    obj_recipe = get_object_or_404(model_object, id=pk)
    obj_subscription = get_object_or_404(model_object, id=pk)

    if model_for_delete_object is Subscription:
        object = get_object_or_404(
            model_for_delete_object, user=user, author=obj_subscription
        )
    else:
        object = get_object_or_404(
            model_for_delete_object, user=user, recipe=obj_recipe
        )
    object.delete()