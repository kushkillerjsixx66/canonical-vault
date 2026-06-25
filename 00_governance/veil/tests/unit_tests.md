# Veil Unit Tests  
*Tests for individual components*

---

## 1. Level Resolver Tests

- resolves Veil-0 for operator surfaces  
- resolves Veil-2 for narrative surfaces  
- rejects invalid levels  
- rejects upward visibility without operator intent  

---

## 2. Redaction Engine Tests

- redacts sensitive fields for Veil-3  
- preserves structure  
- preserves lineage  
- reversible for Veil-0 → Veil-2  

---

## 3. Compression Engine Tests

- compresses narrative artifacts  
- preserves semantic integrity  
- reversible for Veil-2  

---

## 4. Enforcement Layer Tests

- enforces profile limits  
- blocks cross-surface violations  
- logs enforcement events
