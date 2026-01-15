from ursina import * # type: ignore
import random
from ai_pilot import AIPilot 

# --- KALMAN FİLTRESİ ---
class KalmanFiltresi:
    def __init__(self, R=1, Q=0.1):
        self.R = R; self.Q = Q; self.A = 1; self.C = 1; self.x = 0; self.p = 1
    def filtrele(self, olcum):
        tahmin_x = self.A * self.x
        tahmin_p = (self.A * self.p * self.A) + self.Q
        K = tahmin_p * self.C / ((self.C * tahmin_p * self.C) + self.R)
        self.x = tahmin_x + K * (olcum - (self.C * tahmin_x))
        self.p = (1 - K * self.C) * tahmin_p
        return self.x

# --- KURULUM ---
pilot = AIPilot()
pilot.egit() 

app = Ursina()
Sky() 

# --- [MODEL: TURUNCU KUTU] ---
ucak = Entity(model='cube', color=color.orange, texture='white_cube', scale=Vec3(3, 0.5, 2))
sag_kanat = Entity(parent=ucak, model='cube', color=color.black, scale=Vec3(0.2, 0.2, 0.2), position=Vec3(0.6, 0, 0))
sol_kanat = Entity(parent=ucak, model='cube', color=color.black, scale=Vec3(0.2, 0.2, 0.2), position=Vec3(-0.6, 0, 0))

# Arayüz
durum_paneli = Text(text="SISTEM HAZIR", position=Vec2(-0.8, 0.45), scale=1.2)
uyari_yazisi = Text(text="", position=Vec2(0, 0.3), scale=2, color=color.red, origin=(0,0))

# Değişkenler
kalman_pitch = KalmanFiltresi(R=15, Q=0.1)
kalman_roll = KalmanFiltresi(R=15, Q=0.1)
hedef_pitch = 0
hedef_roll = 0
otopilot_kilitli = False 
son_tehlike_tipi = 0 

def update():
    global hedef_pitch, hedef_roll, otopilot_kilitli, son_tehlike_tipi

    # 1. Gürültü ve Filtreleme
    gurultulu_pitch = hedef_pitch + random.uniform(-2, 2)
    gurultulu_roll = hedef_roll + random.uniform(-2, 2)
    temiz_pitch = kalman_pitch.filtrele(gurultulu_pitch)
    temiz_roll = kalman_roll.filtrele(gurultulu_roll)

    # 2. YAPAY ZEKA ANALİZİ
    durum = pilot.analiz_et(temiz_pitch, temiz_roll)

    # Kilit yoksa ve tehlike varsa kilitle
    if not otopilot_kilitli and durum != 0:
        otopilot_kilitli = True
        son_tehlike_tipi = durum 

    # --- OTOPİLOT MODU ---
    if otopilot_kilitli:
        ucak.color = color.red
        durum_paneli.text = f"DURUM: KİLİTLENDİ\nAI Yavaşça Düzeltiyor..."
        
        # Düzeltme Hızı: 0.02
        hedef_pitch = lerp(hedef_pitch, 0, 0.02) 
        hedef_roll = lerp(hedef_roll, 0, 0.02)

        # [DÜZELTME BURADA]: Mantığı ters çevirdik.
        # Eğer temiz_pitch > 0 ise (Pozitif), uçak dalışta demektir -> "BURNU KALDIR" demeli.
        # Eğer temiz_pitch < 0 ise (Negatif), uçak tırmanışta demektir -> "BURNU EZ" demeli.
        
        if son_tehlike_tipi == 1: # Pitch Hatası
            if temiz_pitch > 0: 
                uyari_yazisi.text = "OTOPİLOT: BURNU KALDIRIYOR (Yukarı Çekiyor)..."
            else: 
                uyari_yazisi.text = "OTOPİLOT: BURNU EZİYOR (Aşağı İtiyor)..."
        
        elif son_tehlike_tipi == 2: # Roll Hatası
            uyari_yazisi.text = "OTOPİLOT: KANATLAR DÜZELTİLİYOR..."

        # Kilit Açma
        if abs(temiz_pitch) < 5 and abs(temiz_roll) < 5:
            otopilot_kilitli = False 
            son_tehlike_tipi = 0 
            
    # --- MANUEL MOD ---
    else:
        ucak.color = color.orange
        uyari_yazisi.text = ""
        durum_paneli.text = f"DURUM: GUVENLI\nPITCH: {int(temiz_pitch)}\nROLL: {int(temiz_roll)}"
        
        if held_keys['up arrow']: hedef_pitch += 1 # type: ignore
        if held_keys['down arrow']: hedef_pitch -= 1 # type: ignore
        if held_keys['left arrow']: hedef_roll -= 1 # type: ignore
        if held_keys['right arrow']: hedef_roll += 1 # type: ignore

    # Sınırlama ve Görselleştirme
    hedef_pitch = clamp(hedef_pitch, -90, 90)
    hedef_roll = clamp(hedef_roll, -90, 90)
    
    ucak.rotation_x = temiz_pitch
    ucak.rotation_z = temiz_roll
    camera.rotation_x = temiz_pitch * 0.2

EditorCamera()
app.run() # type: ignore