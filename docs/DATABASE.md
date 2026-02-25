# 🗄️ ESTRUCTURA DE DATOS — ODISEO MVP

Este documento define la arquitectura de persistencia para usuarios, suscripciones y oportunidades de Odiseo.

## 📐 Diagrama Entidad-Relación (ER)

```text
  [ users ] 1 --------- 1 [ subscriptions ]
      | (id)                  (user_id)
      |
      | 1 --------- 1 [ telegram_users ]
      | (id)                  (user_id)

  [ opportunities ] (Feeds independientes)
```

## 📋 Descripción de Tablas

### 1. `users`
Contiene la identidad básica del usuario.
- `id`: UUID o identificador único.
- `email`: Correo electrónico (Unique, Index).
- `password_hash`: Hash de la contraseña.
- `created_at`: Fecha de registro.

### 2. `subscriptions`
Estado de pagos y tiers vía Stripe.
- `user_id`: FK a users.id (PK).
- `stripe_customer_id`: ID de cliente en Stripe (Index).
- `tier`: Nivel de acceso (`free`, `vip`, `pro`).
- `status`: Estado de la suscripción (`active`, `canceled`).
- `expires_at`: Fecha de expiración del periodo pagado.

### 3. `telegram_users`
Mapeo de cuenta web con cuenta de Telegram.
- `user_id`: FK a users.id.
- `telegram_id`: ID numérico de Telegram (Unique, Index).
- `tier`: Sincronizado con la suscripción.

### 4. `opportunities`
Feed central de arbitraje validado.
- `product_id`: SKU del producto.
- `name`: Nombre del producto.
- `price`: Precio actual en tienda.
- `gap_teorico`: % diferencia mercado.
- `margen_odiseo`: % margen neto (Gap - 5%).
- `stock_validado`: Booleano (1=Sí, 0=No).

---

## 🛠️ Debugging & Queries Útiles

### Ver usuarios VIP activos
```sql
SELECT u.email, s.tier, s.expires_at 
FROM users u 
JOIN subscriptions s ON u.id = s.user_id 
WHERE s.tier = 'vip' AND s.status = 'active';
```

### Top 10 Oportunidades del día
```sql
SELECT name, price, margen_odiseo 
FROM opportunities 
WHERE confirmed_at >= date('now') 
ORDER BY margen_odiseo DESC LIMIT 10;
```

### Vincular Telegram ID a usuario
```sql
INSERT INTO telegram_users (user_id, telegram_id, tier) 
VALUES ('user_abc', '123456789', 'pro');
```

---
*Mantenido por el equipo de Core Database — Odiseo v2.0*
