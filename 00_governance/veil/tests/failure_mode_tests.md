# Veil Failure Mode Tests  
*Tests for governed failure behavior*

---

## 1. Enforcement Failures

- invalid veil level → halt + lineage  
- profile violation → halt + lineage  
- surface mismatch → silence protocol  

---

## 2. Redaction Failures

- irreversible redaction without intent → block  
- missing lineage → block  

---

## 3. Compression Failures

- semantic loss → block  
- structural corruption → block
