# Demo kullanıcıları

MVP sunumu için **4 giriş** yeterlidir. Ortak şifre: `Secret12`

| # | E-posta | Rol | Ne için |
|---|---------|-----|---------|
| 1 | `admin@agritwin.demo` | admin | `/admin` yönetim paneli (A01–A08) |
| 2 | `ciftci@agritwin.demo` | farmer | Ana dikey dilim: Domates Serası, AI, senaryo, sanal sulama |
| 3 | `ziraat@agritwin.demo` | agronomist | İkinci hesap / danışman arazisi; admin kullanıcı listesi |
| 4 | `kooperatif@agritwin.demo` | cooperative | Kooperatif rolü; destek talebi vb. |

`consultant` rolü UI’da seçilebilir ama ayrı demo hesabı şart değil (çiftçi/ziraat ile aynı app shell).

## Oluşturma

```bash
cd backend
# Windows
.venv\Scripts\python.exe -m scripts.seed_demo
```

Hesaplar e-posta doğrulanmış gelir; doğrulama kodu gerekmez.

## Önerilen demo sırası

1. **Admin** → KPI, kullanıcılar, cihaz filosu, destek  
2. **Çiftçi** → Domates Serası → canlı sensör / AI / senaryo / sulama (onay şart)  
3. (İsteğe bağlı) **Ziraat** veya **Kooperatif** → rol değişimi
