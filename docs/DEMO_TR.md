# İki dakikalık demo anlatımı

## Açılış

“AI geliştirme süresini kısaltabilir. Bu uygulama, hızın kalite kontrollerini görünmez hale getirmemesi için geliştirdiğim bir yayın hazırlık prototipi.”

## Akış

1. Değişiklik özetinde iş sonucunu, etkilenen alanları ve kabul kriterlerini göster.
2. Test, gizli anahtar taraması, veri incelemesi, geri dönüş planı ve izleme kanıtlarını göster.
3. Gate Decision sekmesinde varsayılan sonucun **REVIEW REQUIRED** olduğunu belirt: kontrollerin geçmesi insan onayını kaldırmıyor.
4. Başarısız test sayısını 1 yap. Sonuç **BLOCKED** olur ve onay düğmesi kapanır.
5. Testi tekrar 0 yap, reviewer gir ve sürümü onayla. JSON ve Markdown çıktıları açılır.
6. İş sonucunda küçük bir değişiklik yap. Önceki onayın geçersiz olduğunu göster.

## Vurgulanacak kararlar

- Puan kritik bir hatayı örtemiyor.
- Model yalnızca ek test fikri önerebiliyor; yayın kararını değiştiremiyor.
- Onay bir kişi adına değil, paketin tam sürümüne bağlanıyor.
- Uygulama gerçek bir deployment yapmıyor ve bunu açıkça söylüyor.

## Muhtemel görüşme sorusu

**Bunu üretime nasıl alırdın?**

Kimlik doğrulama, CI ve güvenlik tarayıcılarından imzalı kanıt, kurumun risk politikasına göre kontrol yönetimi, istisna onayı, kalıcı audit log ve deployment sistemiyle yetkili entegrasyon eklerdim. İlk pilotu deployment tetiklemeden, yalnızca mevcut değişikliklerin gölge değerlendirmesiyle başlatırdım.
