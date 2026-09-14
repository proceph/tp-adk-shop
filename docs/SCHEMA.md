# Base de données — aide-mémoire

Connexion depuis tes tools : rôle `student`, **lecture seule** (`SELECT` uniquement).
Adminer : http://localhost:8081 — serveur `db`, utilisateur `student`, mot de passe `student`, base `shop`.

## Tables

```
categories(id, name, slug)
products(id, sku, name, description, brand, category_id → categories, price_cents, created_at)
inventory(product_id → products, warehouse, quantity_available, quantity_reserved)   -- clé : (product_id, warehouse)
customers(id, email, full_name, city, loyalty_tier, created_at)
orders(id, customer_id → customers, status, total_cents, created_at)
order_items(id, order_id → orders, product_id → products, quantity, unit_price_cents)
product_reviews(id, product_id → products, rating, comment, created_at)
```

Volumétrie : 8 catégories · 180 produits · 60 clients · 300 commandes · 700 avis.

## Ce qu'il faut savoir

- **Les prix sont en centimes** (`price_cents`, `total_cents`, `unit_price_cents`).
- **Le stock vendable, c'est `quantity_available - quantity_reserved`.**
  `quantity_available` compte aussi ce qui est déjà réservé par d'autres commandes.
- Un produit est stocké dans **1 à 3 entrepôts** (`Roubaix`, `Lyon`, `Bordeaux`).
  Le stock d'un produit est donc une **somme**, jamais une seule ligne.
- `orders.status` : `pending`, `paid`, `shipped`, `delivered`, `cancelled`.
- `customers.loyalty_tier` : `bronze`, `silver`, `gold`.
- `product_reviews.rating` : entier de 1 à 5. Tous les produits n'ont pas d'avis.

## Repères de test

| Donnée | Valeur |
|---|---|
| Client de référence | `alice@example.com` (Alice Martin, Paris, gold) |
| Produit de référence | `AUD-0174` — Casque filaire Orion Air, 29,80 € |
| Catalogue complet | 180 produits |

## Requêtes utiles

```sql
-- Stock vendable d'un produit, tous entrepôts confondus
SELECT p.sku, sum(i.quantity_available - i.quantity_reserved) AS vendable
FROM products p JOIN inventory i ON i.product_id = p.id
WHERE p.sku = 'AUD-0174' GROUP BY p.sku;

-- Les mieux notés, en ignorant les produits à moins de 3 avis
SELECT p.sku, p.name, round(avg(r.rating), 2) AS note, count(r.id) AS avis
FROM products p JOIN product_reviews r ON r.product_id = p.id
GROUP BY p.sku, p.name HAVING count(r.id) >= 3
ORDER BY avg(r.rating) DESC LIMIT 5;
```
