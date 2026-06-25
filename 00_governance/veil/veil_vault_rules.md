# Veil Vault Rules  
*Governed veil behavior inside the Vault lifecycle*

The Vault enforces veil rules at every stage of artifact lifecycle.

---

## 1. Commit Stage
- artifact must declare veil level  
- veil metadata must be validated  
- no upward visibility without operator intent  

---

## 2. Review Stage
- reviewers may raise veil level  
- reviewers may not lower veil level without lineage  
- veil enforcement must be logged  

---

## 3. Canonization Stage
- veil level becomes immutable  
- redaction becomes irreversible  
- compression becomes canonical  

---

## 4. Archive Stage
- veil metadata stored with artifact  
- veil lineage preserved  
- visibility history retained  

---

## Purpose
These rules ensure:

- safe archival  
- governed exposure  
- irreversible public-surface protection
