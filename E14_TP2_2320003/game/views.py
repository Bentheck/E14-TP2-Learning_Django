from django.shortcuts import render, get_object_or_404, redirect
from .models import Drug, Zone, DrugAvailability, Player, DrugPrice
from django.db import transaction
from decimal import Decimal
import random

def index(request):
    # Obtenir zone_id à partir de GET ou de la session
    zone_id = request.GET.get('zone_id') or request.session.get('zone_id')
    if not zone_id:
        zone_id = Zone.objects.first().id

    # Récupérer la zone
    zone = get_object_or_404(Zone, id=zone_id)

    player = get_player()

    # Récupérer les médicaments et les zones
    drugs = Drug.objects.all()
    zones = Zone.objects.all()

    # Récupérer les prix des médicaments à partir du modèle DrugPrice
    drug_prices = {}
    for drug in drugs:
        try:
            buy_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='buy').price
            sell_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='sell').price
            drug_prices[drug.id] = {'buy': buy_price, 'sell': sell_price}
        except DrugPrice.DoesNotExist:
            # Gérer les cas où les entrées de prix sont manquantes
            drug_prices[drug.id] = {'buy': 'N/A', 'sell': 'N/A'}

    # Récupérer l'inventaire du joueur à partir de Drug.stock
    player_drugs = Drug.objects.filter(stock__gt=0)

    zone_stock = DrugAvailability.objects.filter(zone=zone).select_related('drug')

    context = {
        'drugs': [(drug, drug_prices.get(drug.id, {'buy': 'N/A', 'sell': 'N/A'})) for drug in drugs],
        'zone': zone,
        'zones': zones,
        'zone_stock': zone_stock,
        'player_money': player.money,
        'player_inventory': {drug: drug.stock for drug in player_drugs},
    }
    return render(request, 'game/index.html', context)

def get_player():
    player, created = Player.objects.get_or_create(id=1)  # Suppose qu'il n'y a qu'un seul joueur
    return player

def change_zone(request):
    zone_id = request.GET.get('zone_id')
    if zone_id:
        request.session['zone_id'] = zone_id
    refresh_drug_availability()
    populate_drug_prices()
    return redirect('index')

def refresh_drug_availability():
    zones = Zone.objects.all()
    drugs = Drug.objects.all()
    updates = []
    MIN_STOCK_LEVEL = 0 

    with transaction.atomic():  # Assurer l'atomicité de l'opération en bloc
        for zone in zones:
            for drug in drugs:
                try:
                    availability = DrugAvailability.objects.get(drug=drug, zone=zone)
                except DrugAvailability.DoesNotExist:
                    print(f"Error: DrugAvailability record for Drug: {drug.name}, Zone: {zone.name} does not exist.")
                    continue

                # Générer une valeur de stock aléatoire supérieure à MIN_STOCK_LEVEL
                new_stock = random.randint(MIN_STOCK_LEVEL, 5000)
                if availability.stock != new_stock:  # Vérifier si une mise à jour est nécessaire
                    availability.stock = new_stock
                    updates.append(availability)
                    print(f"Updated - Drug: {availability.drug.name}, Zone: {availability.zone.name}, New Stock: {new_stock}")

        # Exécuter la mise à jour en bloc si des mises à jour sont nécessaires
        if updates:
            DrugAvailability.objects.bulk_update(updates, ['stock'])
            print(f"Bulk update performed for {len(updates)} entries.")
        else:
            print("No updates needed.")

def populate_drug_prices():
    with transaction.atomic():  # Assurer l'atomicité de l'opération en bloc
        for drug in Drug.objects.all():
            for zone in Zone.objects.all():
                # Récupérer la disponibilité actuelle
                availability = DrugAvailability.objects.filter(drug=drug, zone=zone).first()
                available_stock = Decimal(availability.stock) if availability else Decimal(0)

                # Calculer les prix d'achat et de vente en fonction de la disponibilité avec un facteur de volatilité
                if available_stock > 0:
                    # Une disponibilité plus faible devrait entraîner des prix plus élevés
                    # Augmenter l'impact du facteur de disponibilité
                    availability_factor = Decimal(1) / (available_stock + Decimal(1))
                    base_multiplier = Decimal(random.uniform(1.5, 2.0))  # Varie le multiplicateur de base pour plus de volatilité
                    
                    # Calculer le prix d'achat avec un impact plus fort
                    buy_price = drug.base_price * (base_multiplier + availability_factor * Decimal(200))  # Augmenter le multiplicateur de facteur de disponibilité
                    # Calculer le prix de vente avec un coefficient de profit ajusté
                    sell_price = buy_price * Decimal(random.uniform(0.75, 0.85))  # Augmenter la marge de profit
                else:
                    # Même pour les stocks faibles, ajuster les prix avec plus de volatilité
                    buy_price = drug.base_price * Decimal(random.uniform(2.0, 3.0))  # Augmenter la plage pour les prix d'achat
                    sell_price = buy_price * Decimal(random.uniform(0.8, 0.9))  # Ajuster la marge de profit

                # Mettre à jour ou créer des entrées DrugPrice pour les prix d'achat et de vente
                buy_price_entry, created_buy = DrugPrice.objects.update_or_create(
                    drug=drug,
                    zone=zone,
                    price_type='buy',
                    defaults={'price': buy_price}
                )
                sell_price_entry, created_sell = DrugPrice.objects.update_or_create(
                    drug=drug,
                    zone=zone,
                    price_type='sell',
                    defaults={'price': sell_price}
                )

                # Journalisation des prix créés ou mis à jour
                if created_buy:
                    print(f"Created new buy price for Drug: {drug.name}, Zone: {zone.name}, Price: {buy_price}")
                else:
                    print(f"Updated buy price for Drug: {drug.name}, Zone: {zone.name}, Price: {buy_price}")

                if created_sell:
                    print(f"Created new sell price for Drug: {drug.name}, Zone: {zone.name}, Price: {sell_price}")
                else:
                    print(f"Updated sell price for Drug: {drug.name}, Zone: {zone.name}, Price: {sell_price}")



def buy_drug(request, drug_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        drug = get_object_or_404(Drug, id=drug_id)
        zone_id = request.session.get('zone_id', None)
        zone = get_object_or_404(Zone, id=zone_id) if zone_id else Zone.objects.first()
        player = get_player()

        if quantity > 0:
            buy_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='buy').price
            total_cost = buy_price * Decimal(quantity)

            if player.money >= total_cost:
                try:
                    availability = DrugAvailability.objects.get(drug=drug, zone=zone)
                    if availability.stock >= quantity:
                        # Mettre à jour le stock de médicaments du joueur directement
                        drug.stock += quantity  # Modifier le stock de médicaments du joueur
                        availability.stock -= quantity  # Diminuer la disponibilité dans la zone

                        player.money -= total_cost  # Déduire de l'argent du joueur

                        # Enregistrer les modifications
                        drug.save()  # S'assurer que l'instance du médicament est enregistrée
                        availability.save()
                        player.save()

                        return redirect('index')
                    else:
                        error = 'Not enough stock available in the zone.'
                except DrugAvailability.DoesNotExist:
                    error = 'Drug not available in the selected zone.'
            else:
                error = 'Not enough money to complete the purchase.'
        else:
            error = 'Invalid quantity.'

        # Obtenir zone_id à partir de GET ou de la session
        zone_id = request.GET.get('zone_id') or request.session.get('zone_id')
        if not zone_id:
            zone_id = Zone.objects.first().id

        # Récupérer la zone
        zone = get_object_or_404(Zone, id=zone_id)

        player = get_player()

        # Récupérer les médicaments et les zones
        drugs = Drug.objects.all()
        zones = Zone.objects.all()

        # Récupérer les prix des médicaments à partir du modèle DrugPrice
        drug_prices = {}
        for drug in drugs:
            try:
                buy_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='buy').price
                sell_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='sell').price
                drug_prices[drug.id] = {'buy': buy_price, 'sell': sell_price}
            except DrugPrice.DoesNotExist:
                # Gérer les cas où les entrées de prix sont manquantes
                drug_prices[drug.id] = {'buy': 'N/A', 'sell': 'N/A'}

        # Récupérer l'inventaire du joueur à partir de Drug.stock
        player_drugs = Drug.objects.filter(stock__gt=0)

        zone_stock = DrugAvailability.objects.filter(zone=zone).select_related('drug')

        context = {
            'drugs': [(drug, drug_prices.get(drug.id, {'buy': 'N/A', 'sell': 'N/A'})) for drug in drugs],
            'zone': zone,
            'zones': zones,
            'zone_stock': zone_stock,
            'player_money': player.money,
            'player_inventory': {drug: drug.stock for drug in player_drugs},
        }
        return render(request, 'game/index.html', context)

def sell_drug(request, drug_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        drug = get_object_or_404(Drug, id=drug_id)
        zone_id = request.session.get('zone_id', None)
        zone = get_object_or_404(Zone, id=zone_id) if zone_id else Zone.objects.first()
        player = get_player()

        if quantity > 0 and drug.stock >= quantity:
            sell_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='sell').price
            total_earnings = sell_price * Decimal(quantity)

            # Mettre à jour le médicament et l'inventaire du joueur
            drug.stock -= quantity
            player.money += total_earnings

            # Assurer la mise à jour du stock du médicament et de sa disponibilité
            availability, created = DrugAvailability.objects.get_or_create(drug=drug, zone=zone)
            availability.stock += quantity

            drug.save()
            availability.save()
            player.save()

            return redirect('index')
        else:
            error = 'Invalid quantity or insufficient stock.'

        # Obtenir zone_id à partir de GET ou de la session
        zone_id = request.GET.get('zone_id') or request.session.get('zone_id')
        if not zone_id:
            zone_id = Zone.objects.first().id

        # Récupérer la zone
        zone = get_object_or_404(Zone, id=zone_id)

        player = get_player()

        # Récupérer les médicaments et les zones
        drugs = Drug.objects.all()
        zones = Zone.objects.all()

        # Récupérer les prix des médicaments à partir du modèle DrugPrice
        drug_prices = {}
        for drug in drugs:
            try:
                buy_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='buy').price
                sell_price = DrugPrice.objects.get(drug=drug, zone=zone, price_type='sell').price
                drug_prices[drug.id] = {'buy': buy_price, 'sell': sell_price}
            except DrugPrice.DoesNotExist:
                # Gérer les cas où les entrées de prix sont manquantes
                drug_prices[drug.id] = {'buy': 'N/A', 'sell': 'N/A'}

        # Récupérer l'inventaire du joueur à partir de Drug.stock
        player_drugs = Drug.objects.filter(stock__gt=0)

        zone_stock = DrugAvailability.objects.filter(zone=zone).select_related('drug')

        context = {
            'drugs': [(drug, drug_prices.get(drug.id, {'buy': 'N/A', 'sell': 'N/A'})) for drug in drugs],
            'zone': zone,
            'zones': zones,
            'zone_stock': zone_stock,
            'player_money': player.money,
            'player_inventory': {drug: drug.stock for drug in player_drugs},
        }
        return render(request, 'game/index.html', context)

def clear_session(request):
    request.session.flush()  # Clear all session data
    return redirect('index')  # Redirect to a view, like the home page
