from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from .models import Inventory
from .forms import AddInventory, UpdateInventory
from django.contrib import messages
from django_pandas.io import read_frame
import plotly
import json
import plotly.express as px

# Create your views here.
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def inventory_list(request):
    inventories= Inventory.objects.all()
    context={
        "title":"Inventory List",
        "inventories":inventories
    }
    return render(request, "inventory/inventory_list.html", context=context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def per_product_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context={
        "title" : "Product View",
        "inventory":inventory 
    }
    return render(request, "inventory/per_product.html", context=context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if request.method == "POST":
        add_form = AddInventory(data=request.POST)
        if add_form.is_valid():
            new_inventory = add_form.save(commit = False)
            new_inventory.sales = float(add_form.data['cost_per_item']) * float(add_form.data['quantity_sold'])
            new_inventory.save()
            messages.success(request, "Successfully Added Product")
            return redirect('inventory_list')
    else:
        add_form=AddInventory()

    context = {
        "title" : "Add Product",
        'form' : add_form
    }

    return render(request, 'inventory/add_inv.html', context=context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_product(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.warning(request, "Product Deleted")
    return redirect('inventory_list')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_product(request, pk):
    update_inventory = get_object_or_404(Inventory, pk=pk) 
    if request.method == "POST":
        update_form = UpdateInventory(data=request.POST)
        if update_form.is_valid():
            update_inventory.name = update_form.data['name']
            update_inventory.cost_per_item = update_form.data['cost_per_item']
            update_inventory.quantity_in_stock = update_form.data['quantity_in_stock']
            update_inventory.quantity_sold = update_form.data['quantity_sold']
            update_inventory.sales = float(update_inventory.cost_per_item) * float(update_inventory.quantity_sold )
            update_inventory.save()
            messages.success(request, "Successfully Updated Product")
            return redirect(f'http://127.0.0.1:8000/app/per_product/{pk}')
    else:
        update_form=UpdateInventory(instance=update_inventory)

    context = {
        "title" : "Update Product",
        'form' : update_form
    }

    return render(request, 'inventory/update_inv.html', context=context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    inventories = Inventory.objects.all()

    df = read_frame(inventories)

    sales_graph = df.groupby(by = "last_sales_date", as_index=False, sort=False)['sales'].sum()
    sales_graph = px. line(sales_graph, x=sales_graph.last_sales_date, y = sales_graph.sales, title = "Sales Trend")
    sales_graph = json.dumps(sales_graph, cls=plotly.utils.PlotlyJSONEncoder)

    best_product= df.groupby(by = "name").sum().sort_values(by = 'quantity_sold')
    best_product= px. bar(best_product, x=best_product.index, y = best_product.quantity_sold, title = "Best Performing Product")
    best_product= json.dumps(best_product, cls=plotly.utils.PlotlyJSONEncoder)

    most_product_in_stock= df.groupby(by = "name").sum().sort_values(by = 'quantity_sold')
    most_product_in_stock= px. pie(most_product_in_stock, names= most_product_in_stock.index, values= most_product_in_stock.quantity_sold, title = "Most Product In Stock")
    most_product_in_stock= json.dumps(most_product_in_stock, cls=plotly.utils.PlotlyJSONEncoder)


    context = {
        "sales_graph" : sales_graph,
        "best_product": best_product,
        "most_product_in_stock": most_product_in_stock
    }    

    return render(request, "inventory/dashboard.html", context=context)