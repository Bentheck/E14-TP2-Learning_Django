from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Drug, Zone, DrugAvailability, DrugPrice
from decimal import Decimal
import random


@receiver(post_migrate)
def populate_zones(sender, **kwargs):
    if sender.name == 'game': 
        greater_montreal_zones = [
            "Montreal",
            "Laval",
            "Longueuil",
            "Brossard",
            "Terrebonne",
            "Blainville",
            "Saint-Jérôme",
            "Vaudreuil-Dorion",
            "Repentigny",
            "Dollard-des-Ormeaux",
            "Pointe-Claire",
            "Lachine",
            "LaSalle",
            "Anjou",
            "Outremont",
            "Rosemont-La Petite-Patrie",
            "Mont-Royal",
            "Saint-Laurent",
            "Saint-Michel",
            "Verdun",
            "Ville-Marie",
            "Montreal-Nord",
        ]

        for zone_name in greater_montreal_zones:
            Zone.objects.get_or_create(name=zone_name)

        print("Greater Montreal zones added successfully.")

@receiver(post_migrate)
def populate_drugs(sender, **kwargs):
    drugs = [
        {"name": "Frostbite", "base_price": 100.00, "stock": 0},
        {"name": "Shadow Dust", "base_price": 150.00, "stock": 0},
        {"name": "Firestorm", "base_price": 80.00, "stock": 0},
        {"name": "Moonbeam", "base_price": 20.00, "stock": 0},
        {"name": "Starshine", "base_price": 15.00, "stock": 0},
        {"name": "Mystic Cap", "base_price": 50.00, "stock": 0},
        {"name": "Blaze", "base_price": 120.00, "stock": 0},
        {"name": "Eclipse", "base_price": 200.00, "stock": 0},
        {"name": "Nebula", "base_price": 30.00, "stock": 0},
        {"name": "Twilight", "base_price": 50.00, "stock": 0},
        {"name": "Zenith", "base_price": 100.00, "stock": 0},
        {"name": "Tempest", "base_price": 60.00, "stock": 0},
        {"name": "Aurora", "base_price": 200.00, "stock": 0},
        {"name": "Solar Flare", "base_price": 50.00, "stock": 0},
        {"name": "Meteor Pipe", "base_price": 10.00, "stock": 0},
        {"name": "Sunset", "base_price": 75.00, "stock": 0},
        {"name": "Stardust", "base_price": 40.00, "stock": 0},
        {"name": "Lunar Wave", "base_price": 25.00, "stock": 0},
        {"name": "Black Hole", "base_price": 300.00, "stock": 0},
        {"name": "Thunderstrike", "base_price": 80.00, "stock": 0},
        {"name": "Quasar", "base_price": 90.00, "stock": 0},
        {"name": "Nebulon", "base_price": 60.00, "stock": 0},
        {"name": "Vortex", "base_price": 30.00, "stock": 0},
        {"name": "Dragon's Breath", "base_price": 120.00, "stock": 0},
        {"name": "Phantom", "base_price": 40.00, "stock": 0},
        {"name": "Galactic Pulse", "base_price": 250.00, "stock": 0},
        {"name": "Spectral Silk", "base_price": 180.00, "stock": 0},
        {"name": "Warp Drive", "base_price": 10.00, "stock": 0},
        {"name": "Stellar Surge", "base_price": 20.00, "stock": 0},
        {"name": "Star Pop", "base_price": 15.00, "stock": 50},
        {"name": "Celestial Mist", "base_price": 70.00, "stock": 0},
        {"name": "Luminous Flow", "base_price": 60.00, "stock": 0},
        {"name": "Galactic Bliss", "base_price": 90.00, "stock": 0},
        {"name": "Cosmic Wave", "base_price": 120.00, "stock": 0},
        {"name": "Stellar Echo", "base_price": 150.00, "stock": 0},
        {"name": "Nebula Storm", "base_price": 130.00, "stock": 0},
        {"name": "Astral Beam", "base_price": 70.00, "stock": 0},
        {"name": "Euphoria", "base_price": 100.00, "stock": 0},
        {"name": "Orbit", "base_price": 30.00, "stock": 0}
    ]

    for drug_data in drugs:
        Drug.objects.get_or_create(
            name=drug_data["name"],
            defaults={"base_price": drug_data["base_price"], "stock": drug_data["stock"]}
        )

    print("Drugs added successfully.")

@receiver(post_migrate)
def populate_drug_availability(sender, **kwargs):
    if sender.name == 'game':  # S'assurer que cela s'exécute uniquement pour l'application 'game'
        zones = Zone.objects.all()
        drugs = Drug.objects.all()

        # Remplir DrugAvailability
        for drug in drugs:
            for zone in zones:
                DrugAvailability.objects.get_or_create(
                    drug=drug,
                    zone=zone,
                    defaults={'stock': drug.stock}  # Initialiser avec le stock du médicament
                )

@receiver(post_migrate)
def populate_drug_prices(sender, **kwargs):
    if sender.name == 'game':  # S'assurer que cela s'exécute uniquement pour l'application 'game'
        for drug in Drug.objects.all():
            for zone in Zone.objects.all():
                # Récupérer la disponibilité actuelle
                availability = DrugAvailability.objects.filter(drug=drug, zone=zone).first()
                if availability:
                    available_stock = Decimal(availability.stock)
                else:
                    available_stock = Decimal(0)

                # Calculer le prix d'achat en fonction de la disponibilité
                # Une disponibilité plus élevée augmente le prix d'achat
                if available_stock > 0:
                    base_multiplier = Decimal(0.5)  # Multiplicateur de base pour les calculs de prix
                    # Augmenter le prix d'achat avec la disponibilité
                    buy_price = drug.base_price * (base_multiplier + available_stock * Decimal(0.01))
                    # Diminuer le prix de vente avec la disponibilité
                    sell_price = buy_price * Decimal(0.9)
                else:
                    # Si aucun stock n'est disponible, définir les prix sur une valeur par défaut ou gérer selon les besoins
                    buy_price = drug.base_price * Decimal(0.5)  # Prix bas en l'absence de stock
                    sell_price = buy_price * Decimal(1.1)  # Prix de vente par défaut en l'absence de stock

                # Mettre à jour ou créer des entrées DrugPrice pour les prix d'achat et de vente
                DrugPrice.objects.update_or_create(
                    drug=drug,
                    zone=zone,
                    price_type='buy',
                    defaults={'price': buy_price}
                )
                DrugPrice.objects.update_or_create(
                    drug=drug,
                    zone=zone,
                    price_type='sell',
                    defaults={'price': sell_price}
                )