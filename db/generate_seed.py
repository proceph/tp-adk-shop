#!/usr/bin/env python3
"""Génère db/02_seed.sql de façon déterministe.

Le SQL produit est COMMITÉ dans le repo : on ne génère rien au démarrage du
conteneur, pour que `docker compose up` soit instantané et que toute la classe
ait exactement la même base.

Usage : python3 db/generate_seed.py > db/02_seed.sql
"""

import random
from datetime import datetime, timedelta

random.seed(20260914)  # ne JAMAIS changer : les tests dépendent de ce seed

CATEGORIES = [
    ("Audio", "audio"),
    ("Informatique", "informatique"),
    ("Photo", "photo"),
    ("Maison connectée", "maison-connectee"),
    ("Sport", "sport"),
    ("Gaming", "gaming"),
    ("Téléphonie", "telephonie"),
    ("Accessoires", "accessoires"),
]

# (catégorie, type de produit, prix mini en centimes, prix maxi en centimes)
PRODUCT_TYPES = [
    ("audio", "Casque sans fil", 3990, 34990),
    ("audio", "Casque filaire", 1990, 12990),
    ("audio", "Écouteurs Bluetooth", 2490, 27990),
    ("audio", "Enceinte portable", 3490, 39990),
    ("audio", "Barre de son", 9990, 89990),
    ("informatique", "Ordinateur portable", 49900, 249900),
    ("informatique", "Écran 27 pouces", 14900, 79900),
    ("informatique", "Clavier mécanique", 5990, 21990),
    ("informatique", "Souris ergonomique", 2490, 12990),
    ("informatique", "Disque SSD externe", 6990, 34990),
    ("photo", "Appareil photo hybride", 69900, 329900),
    ("photo", "Objectif 50mm", 19900, 119900),
    ("photo", "Trépied carbone", 8990, 44990),
    ("maison-connectee", "Ampoule connectée", 1490, 5990),
    ("maison-connectee", "Thermostat connecté", 9990, 24990),
    ("maison-connectee", "Caméra de surveillance", 4990, 19990),
    ("maison-connectee", "Aspirateur robot", 19900, 89900),
    ("sport", "Montre GPS", 12900, 74900),
    ("sport", "Bracelet d'activité", 3990, 14990),
    ("sport", "Tapis de yoga", 1990, 8990),
    ("gaming", "Manette sans fil", 4490, 17990),
    ("gaming", "Casque gaming", 3990, 29990),
    ("gaming", "Chaise gaming", 14900, 54900),
    ("telephonie", "Smartphone", 19900, 149900),
    ("telephonie", "Coque de protection", 990, 4990),
    ("telephonie", "Chargeur rapide", 1490, 7990),
    ("accessoires", "Sac à dos", 3990, 19990),
    ("accessoires", "Batterie externe", 1990, 9990),
    ("accessoires", "Câble USB-C", 690, 2990),
]

BRANDS = [
    "Aurora", "Boreal", "Cassini", "Delta Nine", "Everest", "Fjord",
    "Granite", "Helios", "Ibis", "Juno", "Kelvin", "Lumen",
    "Meridian", "Nord", "Orion", "Pulsar",
]

ADJECTIVES = ["Pro", "Lite", "Max", "Studio", "Air", "Plus", "Core", "Edge", "One", "X2"]

DESC_FRAGMENTS = [
    "Conçu pour un usage quotidien intensif, il combine robustesse et finition soignée.",
    "Son autonomie généreuse permet de tenir une journée complète sans recharge.",
    "La connectique standard assure une compatibilité avec la majorité des équipements du marché.",
    "Livré avec sa housse de transport et un guide de démarrage rapide en français.",
    "Les matériaux recyclés représentent plus de 40 % de la coque extérieure.",
    "Un mode économie d'énergie se déclenche automatiquement après cinq minutes d'inactivité.",
    "La garantie constructeur de deux ans couvre les défauts de fabrication.",
    "Le réglage se fait en quelques secondes depuis l'application mobile dédiée.",
    "Testé en laboratoire sur plus de dix mille cycles d'utilisation.",
    "Son format compact se glisse sans effort dans un sac à dos ou une sacoche.",
]

WAREHOUSES = ["Roubaix", "Lyon", "Bordeaux"]

FIRST_NAMES = [
    "Alice", "Bruno", "Camille", "David", "Elsa", "Farid", "Gaelle", "Hugo",
    "Ines", "Julien", "Karim", "Laura", "Malik", "Nadia", "Olivier", "Perrine",
    "Quentin", "Rachida", "Samuel", "Thomas", "Ursula", "Victor", "Wassim", "Yasmine",
]
LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Durand", "Leroy",
    "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David", "Bertrand",
    "Roux", "Vincent", "Fournier", "Morel",
]
CITIES = [
    "Paris", "Lyon", "Marseille", "Lille", "Toulouse", "Nantes",
    "Bordeaux", "Strasbourg", "Rennes", "Montpellier",
]
TIERS = ["bronze", "silver", "gold"]

REVIEW_COMMENTS = {
    5: ["Parfait, rien à redire.", "Excellent rapport qualité-prix.", "Je recommande les yeux fermés.",
        "Au-delà de mes attentes.", "Livraison rapide et produit impeccable."],
    4: ["Très bon produit, un petit détail à améliorer.", "Satisfait dans l'ensemble.",
        "Bonne qualité, notice un peu légère.", "Conforme à la description."],
    3: ["Correct sans plus.", "Fait le travail, sans enthousiasme.", "Moyen pour le prix."],
    2: ["Déçu, la finition laisse à désirer.", "Ne correspond pas tout à fait à la description.",
        "Fragile après quelques semaines."],
    1: ["Très déçu, retour immédiat.", "Ne fonctionne pas correctement.", "À éviter."],
}


def esc(text: str) -> str:
    return text.replace("'", "''")


def main() -> None:
    out = []
    w = out.append

    w("-- FICHIER GÉNÉRÉ par db/generate_seed.py — ne pas éditer à la main.")
    w("-- Régénérer avec : python3 db/generate_seed.py > db/02_seed.sql")
    w("")

    # --- catégories ---
    w("INSERT INTO categories (id, name, slug) VALUES")
    rows = [f"    ({i}, '{esc(name)}', '{slug}')" for i, (name, slug) in enumerate(CATEGORIES, 1)]
    w(",\n".join(rows) + ";")
    w("SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));")
    w("")

    slug_to_id = {slug: i for i, (_, slug) in enumerate(CATEGORIES, 1)}

    # --- produits ---
    products = []          # (id, sku, category_slug, price_cents)
    product_rows = []
    used_names = set()
    pid = 0
    base_date = datetime(2025, 1, 6, 9, 0, 0)

    while pid < 180:
        cat_slug, ptype, pmin, pmax = random.choice(PRODUCT_TYPES)
        brand = random.choice(BRANDS)
        adj = random.choice(ADJECTIVES)
        name = f"{ptype} {brand} {adj}"
        if name in used_names:
            continue
        used_names.add(name)
        pid += 1

        price = random.randrange(pmin // 10, pmax // 10) * 10
        sku = f"{cat_slug[:3].upper()}-{pid:04d}"
        description = " ".join(random.sample(DESC_FRAGMENTS, 3))
        created = base_date + timedelta(days=random.randrange(0, 240), hours=random.randrange(0, 10))

        products.append((pid, sku, cat_slug, price, name))
        product_rows.append(
            f"    ({pid}, '{sku}', '{esc(name)}', '{esc(description)}', '{esc(brand)}', "
            f"{slug_to_id[cat_slug]}, {price}, '{created.isoformat()}+00')"
        )

    w("INSERT INTO products (id, sku, name, description, brand, category_id, price_cents, created_at) VALUES")
    w(",\n".join(product_rows) + ";")
    w("SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));")
    w("")

    # --- inventaire : chaque produit dans 1 à 3 entrepôts, certains en rupture totale ---
    inv_rows = []
    out_of_stock_skus = []
    for p_id, sku, _slug, _price, _name in products:
        warehouses = random.sample(WAREHOUSES, random.randint(1, 3))
        # ~8 % des produits sont en rupture partout : matière à gérer le 409.
        totally_out = random.random() < 0.08
        if totally_out:
            out_of_stock_skus.append(sku)
        for wh in warehouses:
            qty = 0 if totally_out else random.choice([0, 0, 3, 7, 12, 25, 40, 60, 120])
            reserved = 0 if qty == 0 else random.randrange(0, min(qty, 5) + 1)
            inv_rows.append(f"    ({p_id}, '{wh}', {qty}, {reserved})")

    w("INSERT INTO inventory (product_id, warehouse, quantity_available, quantity_reserved) VALUES")
    w(",\n".join(inv_rows) + ";")
    w("")
    w("-- Produits en rupture dans TOUS les entrepôts (utiles pour tester le 409) :")
    for sku in out_of_stock_skus[:10]:
        w(f"--   {sku}")
    w("")

    # --- clients : alice@example.com en premier, elle sert de fil rouge dans le TP ---
    customer_rows = [
        "    (1, 'alice@example.com', 'Alice Martin', 'Paris', 'gold', '2025-01-10T10:00:00+00')"
    ]
    customers = [(1, "alice@example.com")]
    seen_emails = {"alice@example.com"}
    cid = 1
    while cid < 60:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}@example.com"
        if email in seen_emails:
            continue
        seen_emails.add(email)
        cid += 1
        city = random.choice(CITIES)
        tier = random.choices(TIERS, weights=[5, 3, 2])[0]
        created = base_date + timedelta(days=random.randrange(0, 200))
        customers.append((cid, email))
        customer_rows.append(
            f"    ({cid}, '{email}', '{esc(first + ' ' + last)}', '{city}', '{tier}', "
            f"'{created.isoformat()}+00')"
        )

    w("INSERT INTO customers (id, email, full_name, city, loyalty_tier, created_at) VALUES")
    w(",\n".join(customer_rows) + ";")
    w("SELECT setval('customers_id_seq', (SELECT MAX(id) FROM customers));")
    w("")

    # --- commandes + lignes ---
    order_rows, item_rows = [], []
    item_id = 0
    price_by_pid = {p[0]: p[3] for p in products}
    for order_id in range(1, 301):
        # Alice a plusieurs commandes garanties : la démo du palier 3 doit toujours marcher.
        customer_id = 1 if order_id <= 5 else random.choice(customers)[0]
        status = random.choices(
            ["pending", "paid", "shipped", "delivered", "cancelled"],
            weights=[1, 3, 3, 6, 1],
        )[0]
        created = base_date + timedelta(days=random.randrange(0, 250), hours=random.randrange(0, 12))

        total = 0
        for _ in range(random.randint(1, 4)):
            item_id += 1
            product_id = random.randint(1, len(products))
            qty = random.randint(1, 3)
            unit = price_by_pid[product_id]
            total += unit * qty
            item_rows.append(f"    ({item_id}, {order_id}, {product_id}, {qty}, {unit})")

        order_rows.append(
            f"    ({order_id}, {customer_id}, '{status}', {total}, '{created.isoformat()}+00')"
        )

    w("INSERT INTO orders (id, customer_id, status, total_cents, created_at) VALUES")
    w(",\n".join(order_rows) + ";")
    w("SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));")
    w("")

    w("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price_cents) VALUES")
    w(",\n".join(item_rows) + ";")
    w("SELECT setval('order_items_id_seq', (SELECT MAX(id) FROM order_items));")
    w("")

    # --- avis : volontairement inégaux, pour que top_rated_products soit intéressant ---
    review_rows = []
    review_id = 0
    for p_id, _sku, _slug, _price, _name in products:
        for _ in range(random.randint(0, 8)):
            review_id += 1
            rating = random.choices([1, 2, 3, 4, 5], weights=[1, 2, 4, 7, 9])[0]
            comment = random.choice(REVIEW_COMMENTS[rating])
            created = base_date + timedelta(days=random.randrange(10, 250))
            review_rows.append(
                f"    ({review_id}, {p_id}, {rating}, '{esc(comment)}', '{created.isoformat()}+00')"
            )

    w("INSERT INTO product_reviews (id, product_id, rating, comment, created_at) VALUES")
    w(",\n".join(review_rows) + ";")
    w("SELECT setval('product_reviews_id_seq', (SELECT MAX(id) FROM product_reviews));")

    print("\n".join(out))


if __name__ == "__main__":
    main()
