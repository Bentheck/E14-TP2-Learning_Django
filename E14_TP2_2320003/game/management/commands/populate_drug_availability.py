def refresh_drug_availability():
    zones = Zone.objects.all()
    drugs = Drug.objects.all()

    for zone in zones:
        for drug in drugs:
            availability, created = DrugAvailability.objects.get_or_create(
                drug=drug,
                zone=zone
            )
            if not created:
                # Simulate random stock changes
                availability.stock = max(0, availability.stock - random.randint(1, 500))
                availability.save()