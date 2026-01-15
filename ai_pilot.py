import random
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# --- YAPAY ZEKA MODÜLÜ (SESSİZ MOD) ---
class AIPilot:
    def __init__(self):
        self.model = None
        self.egitim_durumu = False

    def egit(self, veri_sayisi=5000):
        print(f">> [AI PILOT] Eğitim başlıyor... ({veri_sayisi} veri)")
        
        egitim_verisi = []
        etiketler = []

        # ETİKETLER: 0: Güvenli, 1: Pitch Hatası, 2: Roll Hatası
        for _ in range(veri_sayisi):
            p = random.randint(-90, 90) 
            r = random.randint(-90, 90) 
            
            egitim_verisi.append([p, r])
            
            # --- KURAL SETİ (30 Derece Hassasiyet) ---
            if abs(p) > 30: 
                etiketler.append(1) # Pitch Tehlikesi
            elif abs(r) > 45: 
                etiketler.append(2) # Roll Tehlikesi
            else:
                etiketler.append(0) # Güvenli

        self.model = RandomForestClassifier(n_estimators=100)
        self.model.fit(egitim_verisi, etiketler)
        self.egitim_durumu = True
        print(">> [AI PILOT] Eğitim tamamlandı.")

    def analiz_et(self, pitch, roll):
        if not self.egitim_durumu: return 0
        
        tahmin = self.model.predict([[pitch, roll]]) # type: ignore
        return tahmin[0]