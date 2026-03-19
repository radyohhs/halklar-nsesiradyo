import streamlit as st
import json
import streamlit.components.v1 as components
import os
import asyncio
import re
import unicodedata

try:
    from ably import AblyRest
except Exception:
    AblyRest = None

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="HALKLARIN SESİ RADYOSU", layout="wide")


# 2. GÖRSEL VERİLERİ
# DJ görselleri: DJ adını yaz, karşısına link yapıştır.
# (Küçük/büyük harf, Türkçe karakter, boşluk/altçizgi farklarını tolere eder.)
DJ_IMAGE_URLS = {
    "xalo_56": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/animasyonlar/halil.gif",
    "serhadoo": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/animasyonlar/serhat.jpg",
    "şaşal_bey56": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/animasyonlar/harun.gif",
    "doktorbey56": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/animasyonlar/hamdullah.gif",
    "yusuf": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/animasyonlar/yusuf.gif",
}


IMG = {
    "grup_yorum": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/Grup%20Yorum.jpg",
    "soldan_sesler": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/gemini_generated_image_7s372s7s372s7s37.png",
    "tiyatro": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Radyo%20Tiyatrosu%206/Gemini_Generated_Image_cuudxvcuudxvcuud.png",
    "tasavvuf": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/sufi.jpg",
    "ermeni_ezgileri": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/ermenice.jpg",
    "mozaik": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/Gemini_Generated_Image_ychv77ychv77ychv.png",
    "tsm": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/gemini_generated_image_v8oe83v8oe83v8oe.png",
    "anadolu_rock": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/Gemini_Generated_Image_cn6f9gcn6f9gcn6f.png",
    "ahmet_kaya" :"https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/Gemini_Generated_Image_t4ub36t4ub36t4ub.png"
}

NEWROZ_MSGS = [
    "NEWROZ PÎROZ BE!",
    "NEWROZ KUTLU OLSUN!",
    "NEWROZÊ ŞIMA PÎROZ BO!",
    "Շնորհավոր Նավասարդ․",  # Ermenice
    "ܢܘܪܘܙ ܒܪܝܟܐ! ܚܕ ܢܘܪܘܙܐ ܒܪܝܟܐ",           # Süryanice
    "عيد نوروز سعيد!",
    "نوروز مبارک!"
]

# 3. TÜM LİNKLER - EKSİKSİZ VE ALT ALTA (DÖNGÜSÜZ)

# --- AHMET KAYA (TAM LİSTE) ---
AK = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/acilara_tutunmak_ahmet_kaya_5jhupqfjoac.mp3", "duration": 238},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_basim_belada_qzmnx95myfa.mp3", "duration": 244},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_dogumgunu_cszsqpfbygq.mp3", "duration": 188},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_gel_hadi_gel_w8maklsq1hi.mp3", "duration": 191},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_kacakci_kurban_wm5jfbn2lcs.mp3", "duration": 226},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_kadinlar_yuruyor_daglara_dogru_ukn9q3tstrw.mp3", "duration": 157},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_kalan_kalir_pts6azk763k.mp3", "duration": 223},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_siire_gazele_z8qaeubsir8.mp3", "duration": 244},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ahmet_kaya_kendine_iyi_bak_vp8nmlqfqrq.mp3", "duration": 263},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/ay_gidiyor_ahmet_kaya_vd3s6_xejmk.mp3", "duration": 352},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/baskaldiriyorum_ahmet_kaya_ptl7h0kdp1m.mp3", "duration": 172},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/beni_vur_ahmet_kaya_7wvth8y4xe8.mp3", "duration": 325},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/giderim_ahmet_kaya_j8wbl3dey48.mp3", "duration": 287},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/kod_adi_bahtiyar_ahmet_kaya_orgk6iiqw4g.mp3", "duration": 335},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/icimde_olen_biri_ahmet_kaya_3v4vqogwkza.mp3", "duration": 242},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/kum_gibi_ahmet_kaya_1miwaizwjbk.mp3", "duration": 281},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/mahur_gayc2binl54.mp3", "duration": 317},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ahmet%20Kaya/safak_turkusu_ahmet_kaya_iiway4mc7pk.mp3", "duration": 413}
]

# --- SOLDAN SESLER (TAM LİSTE) ---
SS = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/adalilar_devrim_marsi_l0szt_cnh8o.mp3", "duration": 244},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/bandista_haydi_barikata_ax5nsjo0f9w.mp3", "duration": 186},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/bekci_kazim_turkusu_6rgwd3wxppa.mp3", "duration": 194},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/dev_genc_marsi_x_lbw73uvmk.mp3", "duration": 165},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/elbruz_daglari_antifasist_kafkas_turkusu_et9q0j1o9n4.mp3", "duration": 244},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/ew_ser_sere_meye_rizgariya_me_ye_grup_isyan_atesi_biji_biji_kobane_czg7w_3c_yq.mp3", "duration": 178},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/grup_ekin_istanbul_safaklari_gun_bizim_1993_kalan_muzik_31mcbyjebfc.mp3", "duration": 256},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/grup_ekin_varsa_cesaretiniz_gelin_gun_bizim_1993_kalan_muzik_qxscowxwtp8.mp3", "duration": 201},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/grup_munzur_isyan_atesi_official_music_video_1993_ses_plak_uass4xb8k3i.mp3", "duration": 243},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/grup_ozgurluk_dersim_sdwzkb4hv10.mp3", "duration": 129},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/grup_ozgurluk_suphan_dagi_syu_l_p6f1a.mp3", "duration": 198},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/grup_vardiya_birlik_marsi_dsmmtq3ed6m.mp3", "duration": 225},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/grup_vardiya_ibrahim_yoldas_ibrahimkaypakkaya_18mayis1973_1gqp2xwhqye.mp3", "duration": 264},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/gulcan_altan_omuz_ver_wysww8eseay.mp3", "duration": 220},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/sonbahardan_cizgiler_ofkasxnrwuu.mp3", "duration": 262},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/yeni_turku_beyazit_meydani_ndaki_olu_bugdayinturkusu_adamuzik_oa0x20kedek.mp3", "duration": 236},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/yeni_turku_isci_marsi_bugdayinturkusu_adamuzik_wghv3_8hro4.mp3", "duration": 175},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/yeni_turku_maphusane_kapisi_bugdayinturkusu_adamuzik_sdv8oa59ov8.mp3", "duration": 201},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Soldan%20Sesler/yeni_turku_ozgurluk_bugdayinturkusu_adamuzik_yx5ew6v_dzq.mp3", "duration": 247},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_bir_mayis.mp3", "duration": 215},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_cav_bella.mp3", "duration": 165},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_defol_amerika.mp3", "duration": 145},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_kizildere.mp3", "duration": 215},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_hakliyiz_kazanacagiz.mp3", "duration": 265},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_daglara_gel.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_devrim_yuruyusumuz_suruyor.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_dunya_haklari_kardestir_bu_memleket_bizim.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_dusenlere.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_ellerinde_pankartlar.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_gel_ki_safaklar_tutussun.mp3", "duration": 240},
    
]

# --- GRUP YORUM (TAM LİSTE - TEK TEK) ---
GY = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_avusturya_isci_marsi.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_bagcilar_da_uc_karanfil.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_basegmeden.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_berivan.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_bir_gorus_kabininde....mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_bir_mayis.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_biz_hic_teslim_olmadik_ki.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_bugun_pazar.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_buyu.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_cav_bella.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_cemo.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_daglara_dogru.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_daglara_gel.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_devrim_yuruyusumuz_suruyor.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_dunya_haklari_kardestir_bu_memleket_bizim.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_dusenlere.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_ellerinde_pankartlar.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_gel_ki_safaklar_tutussun.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_gowenda_gelan.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_gun_dogdu.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_hakikat_savascisi.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_hakliyiz_kazanacagiz.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_halkin_elleri.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_hasta_siempre.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_haziranda_olmek_zor.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_ille_kavga.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_ince_memed.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_insan_pazari.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_karadir_kaslarin.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_kizildere.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_le_hanim.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_omuzdan_tutun_beni.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_sahan_kanatlilar.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_selam_olsun.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_sisli_meydaninda_uc_kiz.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_siyrilip_gelen.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_soluk_soluga.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_sur_gerilla.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_ugurlama.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_uyan_berkin.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_uyur_idik_uyardilar.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_uzatin_ellerinizi.mp3", "duration": 240},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Songs/grup_yorum_yarin_bizimdir.mp3", "duration": 240}
]

# --- RADYO TİYATROSU (TAM LİSTE) ---
RT = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Radyo%20Tiyatrosu%201/kapidaki_adam.mp3", "duration": 1800},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Radyo%20Tiyatrosu%202/aci_bal.mp3", "duration": 1800},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Radyo%20Tiyatrosu%203/colde_bir_portakal.mp3", "duration": 1800},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Radyo%20Tiyatrosu%205/yorgun_atlar.mp3", "duration": 1800},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Radyo%20Tiyatrosu%204/bronte_kardesler_anne_bront.mp3", "duration": 1800},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Radyo%20Tiyatrosu%206/Yildizlar%20Barisiyor.mp3", "duration": 1800}
]

# --- TASAVVUF / DEYİŞLER (ÖZEL PLAYLIST) ---
TASAVVUF = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/affet_isyanim_ding_qse0i8.mp3", "duration": 260.62},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/bu_ask_bir_bahri_ummandir_sbykofwdr2a.mp3", "duration": 337.92},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/derman_arardim_derdime_cdezyaefpes.mp3", "duration": 187.22},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/guzel_asik_cevrimizi_eshzeetynh0.mp3", "duration": 373.89},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/kus_dili_sureyya_akay_dem_i_devran_1_utei4rpbafy.mp3", "duration": 205.14},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/sah_hatayi_ozun_egri_ise_yola_zararsin_kzpucljxkrm.mp3", "duration": 275.51},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/sarab_i_askini_nus_ettir_ya_rab_sybn6bvtcos.mp3", "duration": 235.73},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/seni_ben_severim_candan_iceru_rdgn7wrifaw.mp3", "duration": 324.55},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/tefvizname_askin_yolculugu_4scxbavswcc.mp3", "duration": 315.04},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Tasavvuf/uyur_idik_uyardilar_a_mqqooiits.mp3", "duration": 570.54}
]
ERMENICE = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/antsnink_sasun_lets_take_sasun_armenian_revolutionary_patriotic_song_x4z_qsvrzte.mp3", "duration": 230.82},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/ara_dinkjian_ny_gypsy_all_stars_annatolya_homecoming_5vc7fk9_v8k.mp3", "duration": 470.52},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/arax_baleni_av050sam0po.mp3", "duration": 245.11},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/bingyol_ucyf7mj7m_i.mp3", "duration": 178.52},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/collectif_medz_bazar_done_yar_armenian_traditional_song_ao_vivo_na_porta_253_snmptls8tu4.mp3", "duration": 274.68},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/erzeroumi_shoror_00uw9kgz4qm.mp3", "duration": 250.04},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/garik_sona_mayro_official_video_i78nu40y9zq.mp3", "duration": 215.12},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/grup_knar_ermeniyiz_meskanimiz_anadoludan_kafkaslara_ermeni_muzigi_2015_kalan_muzik_1vpmmhd1_la.mp3", "duration": 311.01},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/grup_knar_sasna_saran_anadoludan_kafkaslara_ermeni_muzigi_2015_kalan_muzik_ga6cy9_34ms.mp3", "duration": 362.16},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/ilda_simonian_adana_agidi_fmmugu5f34a.mp3", "duration": 233.59},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/ilda_simonian_bingoli_lq8z50wf97w.mp3", "duration": 200.59},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/ilda_simonian_dagli_gelin_sari_gelin_gftm7c_za7i.mp3", "duration": 173.09},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/kalenderi_dehri_gezsen.mp3", "duration": 305.35},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/knar_ay_nare_nare_nare_yar_jxbbtgnn9fg.mp3", "duration": 383.03},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/knar_ari_ari_ha_ninna_ninno_9qvkp6j85vs.mp3", "duration": 356.13},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/knar_makruhi_can_yuhfsh6ygok.mp3", "duration": 183.07},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/leylum_24kpck99jwy.mp3", "duration": 372.14},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/lilit_pipoyan_gulo_koulo_49ojbh5fnxu.mp3", "duration": 177.14},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/lilit_pipoyan_tsankutiun_wish_sdorjyverbc.mp3", "duration": 194.48},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/nemra_nare_official_video_jyzbcnoxqku.mp3", "duration": 249.05},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/rewsan_liana_benli_salik_snok_mayro_xy79jjdpp94.mp3", "duration": 402.96},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/sareri_hovin_mernem_yvopp5rereq.mp3", "duration": 266.42},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Ermenice/zulal_mer_dan_idev_qnhbb24nvdg.mp3", "duration": 103.05}
]

MOZAIK = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/ana_la_habibi_5uamf21kpk4.mp3", "duration": 180.90},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/anadolu_quartet_sakina_lo_sivono_official_audio_zytri7f8od4.mp3", "duration": 337.21},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/antsnink_sasun_lets_take_sasun_armenian_revolutionary_patriotic_song_x4z_qsvrzte.mp3", "duration": 230.82},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/babetna_khosha_hawraman_sb83_t5ivra.mp3", "duration": 217.29},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/bingyol_ucyf7mj7m_i.mp3", "duration": 178.52},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/e_m_e_l_holm_a_dream_official_video_d2snx3bfykw.mp3", "duration": 285.39},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/emel_mathlouthi_ma_lkit_official_video_gdiz2i_xwt8.mp3", "duration": 237.74},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/emel_mathlouthi_naci_en_palestina_qhswc47rqzm.mp3", "duration": 253.20},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/fairuz_bint_el_shalabiya_briw30_4prm.mp3", "duration": 188.24},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/fairuz_kifak_inta_lyric_video_nvr4lpokqzi.mp3", "duration": 213.47},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/fairuz_le_beirut_8ayx6zspbgg.mp3", "duration": 251.30},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/garik_sona_mayro_official_video_i78nu40_y9zq.mp3", "duration": 215.12},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/grup_knar_sasna_saran_anadoludan_kafkaslara_ermeni_muzigi_2015_kalan_muzik_ga6cy9_34ms.mp3", "duration": 362.16},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/grup_munzur_namag.mp3", "duration": 262.84},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/ilda_simonian_bingoli_lq8z50wf97w.mp3", "duration": 200.59},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/ilda_simonian_dagli_gelin_sari_gelin_gftm7c_za7i.mp3", "duration": 173.09},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/julia_boutros_3aba_majdaka_platea_2014_d2fk_hhtvo.mp3", "duration": 212.87},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/knar_ari_ari_ha_ninna_ninno_9qvkp6j85vs.mp3", "duration": 356.13},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/knar_ay_nare_nare_nare_yar_jxbbtgnn9fg.mp3", "duration": 383.03},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/konna_netlaka_ghyhvqhyevi.mp3", "duration": 203.00},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/lamma_bada_yatathana_3dq6716xkwa.mp3", "duration": 241.53},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/le_xanim_deresore_ax_wey_lo_lorke_8f6x_6e5vby.mp3", "duration": 280.22},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/lena_chamamyan_love_in_damascus_vnjnrcrvjtk.mp3", "duration": 304.33},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/leylum_24kpck99jwy.mp3", "duration": 372.14},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/lilit_pipoyan_gulo_koulo_49ojbh5fnxu.mp3", "duration": 177.14},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/maii_and_zeid_kalam_el_leil_tdvuxpsl33g.mp3", "duration": 168.80},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/mikail_aslan_hamam_petag_dersim_ermeni_halk_sarkilari_2010_kalan_muzik_0iog_bksbfa.mp3", "duration": 198.79},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/mikail_aslan_surp_garabede_gitmisim_petag_2010_kalan_muzik_pwlz3na6kzw.mp3", "duration": 252.03},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/moukawem_vvkbv9awd0o.mp3", "duration": 205.87},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/mourib_zze5lssrr5o.mp3", "duration": 162.74},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/nassam_alayna_el_hawa_2zw1kdmgins.mp3", "duration": 239.75},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/nemra_nare_official_video_jyzbcnoxqku.mp3", "duration": 249.05},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/sahiya_stranan_newroz_e_newroz_e_official_audio_kom_muzik_yfavewtoebi.mp3", "duration": 252.53},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/orange_blossom_ya_sidi_clip_officiel_marseille_g5qe48c_jyu.mp3", "duration": 275.51},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/sahiya_stranan_welat_ci_qas_xwes_rind_e_official_audio_kom_muzik_cfsmd7oq04a.mp3", "duration": 178.96},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/sahiya_stranan_yaramina_bedew_e_official_audio_2nm5nl6cvy0.mp3", "duration": 178.70},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/sareri_hovin_mernem_yvopp5rereq.mp3", "duration": 266.42},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/ya_ana_ya_ana_fairuz_bticppmf1ya.mp3", "duration": 142.29},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/Mozaik/yaveran_mesem_ahura_ritim_toplulugu_2019_sazak_koyu_dv7z6n22wfo.mp3", "duration": 283.30}
]

TSM = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/aksam_oldu_huzunlendim_ben_yine_bulent_ersoy_official_audio_bulentersoy_esen_muzik_kdr7hszqtqg.mp3", "duration": 186.17},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/bahari_bekleyen_kumrular_gibi_bulent_ersoy_official_audio_baharibekleyenkumrulargibi_bulentersoy_hvmlcouil7i.mp3", "duration": 255.97},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/bir_ihtimal_daha_var_qqcravflao0.mp3", "duration": 206.89},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/dok_zulfunu_meydana_gel_munir_nurettin_selcuk_fbq3pap6rx0.mp3", "duration": 132.49},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/erol_buyukburc_inleyen_nagmeler_neredesin_firuze_2004_kalan_muzik_2f_gfjpe_vs.mp3", "duration": 264.54},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/ey_suh_i_sertb_ey_durr_i_nayb_kurdilihicazkar_zbit1m_yizi.mp3", "duration": 140.88},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/gaye_su_akyol_avuclarimda_hala_sicakligin_var_live_feza_musiki_cemiyeti_9xblagtopos.mp3", "duration": 200.67},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/gaye_su_akyol_beyaz_giyme_toz_olur_live_feza_musiki_cemiyeti_coynyrkqsjc.mp3", "duration": 214.94},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/gaye_su_akyol_saymadim_kac_yil_oldu_live_feza_musiki_cemiyeti_8imaqd45ytq.mp3", "duration": 248.01},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/golden_horn_ensemble_evvel_benim_nazli_yarim_karagozun_sarkisi_1996_kalan_muzik_df4fpebzmlc.mp3", "duration": 50.47},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/golden_horn_ensemble_sevdigim_cemalin_cunki_goremem_haremde_nese_1995_kalan_muzik_af7vsr84ln4.mp3", "duration": 136.10},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/hamiyet_yuceses_ada_sahilleri_hjs2ac88org.mp3", "duration": 268.38},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/hersey_seni_hatirlatiyor_y7_xmxrjdd4.mp3", "duration": 345.26},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/huner_coskuner_elveda_meyhaneci_cg0ygu9fkp0.mp3", "duration": 193.15},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/huner_coskuner_gecmesin_gunumuz_0ggyqzmneka.mp3", "duration": 176.64},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/huner_coskuner_sarkilar_seni_soyler_x7tg1pojiio.mp3", "duration": 193.04},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/huner_coskuner_seni_ben_ellerin_olsun_diye_mi_sevdim_sqcjrrahwha.mp3", "duration": 245.00},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/kapildim_gidiyorum_6bl6pa1cwjq.mp3", "duration": 155.32},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/melahat_pars_ben_gamli_hazan_plak_tgapkk4w9so.mp3", "duration": 228.34},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/muzeyyen_senar_dalgalandimda_duruldum_n4je3fvl0ty.mp3", "duration": 281.10},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/muzeyyen_senar_gamzedeyim_deva_bulmam_1975_0ddm0jtfoy8.mp3", "duration": 261.54},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/muzeyyen_senar_omrumuzun_son_demi_hzckloaswlk.mp3", "duration": 206.08},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/muzeyyen_senar_sigaramin_dumani_1975_bxj9dgnj_5e.mp3", "duration": 132.55},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/ne_cikar_bahtimizda_ayrilik_varsa_6wns4p86dvq.mp3", "duration": 171.13},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/nesrin_sipahi_yildizlarin_altinda_official_audio_oh5xh7ipwyc.mp3", "duration": 195.84},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/rusen_yilmaz_benzemez_kimse_sana_fasil_meyhane_sarkilari_dms_muzik_fp31chaocho.mp3", "duration": 212.45},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/samime_sanay_bir_ilkbahar_sabahi_gunesle_uyandinmi_hic_v16cllkd5w4.mp3", "duration": 282.31},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/sevval_sam_soyleyemem_derdimi_i_sek_2006_kalan_muzik_xqs4l3rpgsy.mp3", "duration": 184.71},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/sezen_aksu_istanbul_istanbul_olali_qjywpkobsjo.mp3", "duration": 356.10},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/sezen_aksu_lale_devri_mav2gn_nse4.mp3", "duration": 296.10},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/zeki_muren_ah_bu_sarkilarin_gozu_kor_olsun_ocxfmjngwaa.mp3", "duration": 314.17},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/zeki_muren_elbet_bir_gun_bulusacagiz_te7b_if_bis.mp3", "duration": 308.56},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/zeki_muren_ruyalarda_bulusuruz_1989_5tlmseagrji.mp3", "duration": 365.37},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/zeki_muren_simdi_uzaklardasin_y4bjtepf6tc.mp3", "duration": 201.17},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/TSM/zeki_muren_sorma_ne_haldeyim_gxaa3ag9z8s.mp3", "duration": 252.50}
]

ANADOLU_ROCK = [
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/21_peron_anlatamiyorum_1977_6ne_kzrx0ti.mp3", "duration": 199.78},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/3_hurel_haram_1972_ste3qxximm0.mp3", "duration": 150.91},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/3_hurel_omur_biter_yol_bitmez_1974_gkweq1nxshu.mp3", "duration": 234.06},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/alman_lisesi_gevheri_1970_8fdom8iswog.mp3", "duration": 165.46},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/ankara_fen_lisesi_drama_koprusu_1968_cahdin7yixo.mp3", "duration": 202.53},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/baris_manco_kara_sevda_wskhevpceyi.mp3", "duration": 263.05},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/cem_karaca_1_mayis_butdthvr0hs.mp3", "duration": 250.12},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/cem_karaca_namus_belasi_q_g_72334bg.mp3", "duration": 264.70},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/cem_karaca_ve_apaslar_karanlik_yollar_1968_ydfimmhwytq.mp3", "duration": 218.88},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/cem_karaca_ve_apaslar_resimdeki_gozyaslari_1968_s_gh_nondam.mp3", "duration": 180.74},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/derdiyoklar_ikilisi_otme_bulbul_1984_wv_jcvct0x8.mp3", "duration": 134.03},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/edip_akbayram_ve_dostlar_mehmet_emmi_1976_emgkjhr1vue.mp3", "duration": 298.32},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/erguder_yoldas_gecti_dost_kervani_remastered_official_audio_y0qsysdedum.mp3", "duration": 231.60},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/erkin_koray_bir_eylul_aksami_1966_wkmplzhakqo.mp3", "duration": 164.05},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/ersen_ve_dadaslar_bir_ayrilik_bir_yoksulluk_bir_olum_1974_al7vt5llvzy.mp3", "duration": 259.24},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/ersen_ve_dadaslar_dostlar_beni_hatirlasin_1975_oc7t_sfqvqq.mp3", "duration": 226.09},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/esin_afsar_zuhtu_1976_cxo_z5ayyqg.mp3", "duration": 217.78},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/feylesoflar_biz_insanlar_1975_kktsjg6fnvk.mp3", "duration": 242.13},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/fikret_kizilok_ay_osman_1967_c55exd3ladg.mp3", "duration": 141.66},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/grup_bunalim_tas_var_kopek_yok_1970_jhrkzrrppy4.mp3", "duration": 240.20},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/halicte_gun_batimi_d2mwgktbzpu.mp3", "duration": 250.28},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/hardal_gece_vakti_1980_unpqqq8rdkw.mp3", "duration": 228.02},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/kardaslar_cokertme_1973_ch_e7pege2w.mp3", "duration": 270.03},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/kardaslar_deniz_ustu_kopurur_1973_uvao00zjcrw.mp3", "duration": 373.13},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/lsd_orkestrasi_neye_geldim_dunyaya_1967_j3imtxw8a00.mp3", "duration": 180.04},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/mogollar_alageyik_destani_1972_qmixacbpelc.mp3", "duration": 184.16},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/ozdemir_erdogan_ac_kapiyi_gir_iceri_1974_zgmt_ymuinw.mp3", "duration": 346.02},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/ozdemir_erdogan_gurbet_1972_w0dtblcb9ko.mp3", "duration": 201.17},
    {"url": "https://azcsreefvufvhkzbksyv.supabase.co/storage/v1/object/public/ANADOLU%20ROCK/ozdemir_erdogan_uzun_ince_bir_yoldayim_1973_l61cplav24w.mp3", "duration": 214.15}
]

# 4. YAYIN AKIŞI PROGRAMI
PLAYLISTS = {
    "ahmet_kaya": AK,
    "ermeni_ezgileri": ERMENICE,
    "mozaik": MOZAIK,
    "tsm": TSM,
    "tiyatro": RT,
    "soldan_sesler": SS,
    "tasavvuf": TASAVVUF,
    "anadolu_rock": ANADOLU_ROCK,
    "grup_yorum": GY
}

# Program -> DJ ismi (örnek). İstersen değiştirebilirsin.
DJ_BY_PROGRAM = {
    "ahmet_kaya": "DJ xalo_56",
    "ermeni_ezgileri": "DJ xalo_56",
    "mozaik": "DJ serhadoo",
    "tsm": "DJ şaşal_bey56",
    "tiyatro": "DJ şaşal_bey56",
    "soldan_sesler": "DJ doktorbey56",
    "tasavvuf": "DJ yusuf",
    "anadolu_rock": "DJ yusuf",
    "grup_yorum": "DJ doktorbey56",
}

# Her DJ için chat içinde sabit kalacak mesajlar.
# Not: Python tarafındaki anahtarlar "normalize" sonrası kullanılacaktır;
# 'şaşal_bey56' -> 'sasal_bey56' olur (Türkçe karakterler sadeleşir).
PINNED_DJ_MESSAGES = {
    "xalo_56": "DJ xalo_56 keyifli seyirler diler.",
    "serhadoo": "DJ serhadoo keyifli seyirler diler.",
    "sasal_bey56": "DJ şaşal_bey56 keyifli seyirler diler.",
    "doktorbey56": "DJ doktorbey56 keyifli seyirler diler.",
    "yusuf": "DJ yusuf keyifli seyirler diler.",
}

# Küfür/NSFW kelime listesi (txt dosyasından)
def _load_banned_stems_from_txt(txt_filename: str, cap: int = 5000):
    """
    txt'deki kelimeleri normalize edip boşluksuz (compact) kök/stem olarak JS tarafına gönderir.
    Çok büyük listelerde sayfayı yavaşlatmamak için cap uygulanır.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, txt_filename)
        if not os.path.exists(path):
            return []

        def normalize_for_filter_py(s: str) -> str:
            t = (s or "").lower()
            t = unicodedata.normalize("NFD", t)
            t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")  # diakritikleri sil
            # harf/rakam/boşluk dışında kalanları boşluğa çevir
            t = re.sub(r"[^a-z0-9\\s]+", " ", t)
            t = re.sub(r"\\s+", " ", t).strip()
            return t

        stems = set()
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                raw = line.strip()
                if not raw:
                    continue
                norm = normalize_for_filter_py(raw)
                if not norm:
                    continue
                compact = norm.replace(" ", "")
                if len(compact) < 3:
                    continue
                stems.add(compact)
                if len(stems) >= cap:
                    break

        return list(stems)
    except Exception:
        return []


BANNED_STEMS_FROM_TXT = _load_banned_stems_from_txt("banned_words.txt")

# --- CANLI CHAT (ABLY) ---
# API key'i koda yazma. Şunlardan birine koy:
# - .streamlit/secrets.toml: ABLY_API_KEY="xxx:yyy"
# - veya Windows ortam değişkeni: ABLY_API_KEY
ably_api_key = None
ably_key_source = None
ably_channel = "radyo-chat"

# Streamlit secrets bazen anahtar yoksa exception fırlatabiliyor.
# Site çalışmaya devam etsin diye güvenli okuyoruz.
try:
    if hasattr(st, "secrets"):
        # "in" kontrolü key yoksa fırlatmayı azaltır.
        if "ABLY_API_KEY" in st.secrets:
            ably_api_key = st.secrets["ABLY_API_KEY"]
            ably_key_source = "secrets"
        if "ABLY_CHANNEL" in st.secrets:
            ably_channel = st.secrets["ABLY_CHANNEL"]
except Exception:
    pass

if not ably_api_key:
    _env_key = os.getenv("ABLY_API_KEY")
    if _env_key:
        ably_api_key = _env_key
        ably_key_source = "env"

_env_channel = os.getenv("ABLY_CHANNEL")
if _env_channel:
    ably_channel = _env_channel

ably_token = None
ably_error = None

if not ably_api_key:
    ably_error = "ABLY_API_KEY bulunamadı (secrets/env)."
elif not AblyRest:
    ably_error = "Python 'ably' kütüphanesi yüklenemedi (import)."
else:
    try:
        ably = AblyRest(ably_api_key)
        # Token (kısa ömürlü) üret; çok sekmeli kullanımda TokenRequest'ten daha stabil
        # Capability istemiyoruz: Ably key'in kendi capability'si ile kesişim bazen boş olabiliyor.
        # (40160: Intersection ... is empty)
        _tok = ably.auth.request_token(
            {
                "client_id": "radyo-web",
                # Token çok kısa expire olursa JS tarafında token yenileme
                # mekanizması (authUrl/authCallback/key) olmadığı için hata verir.
                # Bu yüzden TTL'yi olabildiğince uzun tutuyoruz.
                # Not: Ably limits'e göre dönen TTL istenenden kısa olabilir.
                "ttl": 12 * 60 * 60 * 1000,  # 12 saat (ms)
                # Token'ın bu kanala erişmesi için capability'i açıkça belirt.
                # Yapı: { "channel-name": ["publish","subscribe"] }
                "capability": json.dumps(
                    # presence için Ably Presence opsiyonu gerekli
                    {ably_channel: ["publish", "subscribe", "presence"]}
                ),
            }
        )

        if asyncio.iscoroutine(_tok):
            _tok = asyncio.run(_tok)

        # json.dumps için dict'e çevir
        if hasattr(_tok, "to_dict"):
            ably_token = _tok.to_dict()
        elif isinstance(_tok, dict):
            ably_token = _tok
        else:
            ably_token = dict(_tok)
    except Exception as e:
        ably_token = None
        ably_error = f"Token hatası: {type(e).__name__}: {e}"

data_json = json.dumps(
    {
        "playlists": PLAYLISTS,
        "imgs": IMG,
        "newroz": NEWROZ_MSGS,
        "djs": DJ_BY_PROGRAM,
        "djImages": DJ_IMAGE_URLS,
        "pinnedDjMessages": PINNED_DJ_MESSAGES,
        "bannedStemsFromTxt": BANNED_STEMS_FROM_TXT,
        "ablyToken": ably_token,
        "ablyChannel": ably_channel,
        "ablyEnabled": bool(ably_token),
        "ablyError": ably_error,
        "ablyKeySource": ably_key_source,
    }
)

# 5. FINAL ARAYÜZ (HTML & JS)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100dvh; width: 100%; background: #000; color: white; font-family: 'Segoe UI', sans-serif; overflow: hidden; }}

        /* (Geçici telif uyarı bandı kaldırıldı) */

        /* Altta hafif kırmızı kıvılcımlar (2 katman, animasyonlu) */
        body::before {{
            content: "";
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            height: 14dvh;
            pointer-events: none;
            z-index: 2;
            opacity: 0.40;
            filter: blur(0.8px);
            background:
                radial-gradient(circle at 8% 92%, rgba(255, 69, 0, 0.22) 0 1px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 17% 80%, rgba(255, 69, 0, 0.28) 0 2px, rgba(0,0,0,0) 5px),
                radial-gradient(circle at 28% 95%, rgba(255, 69, 0, 0.18) 0 1px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 40% 84%, rgba(255, 69, 0, 0.25) 0 2px, rgba(0,0,0,0) 5px),
                radial-gradient(circle at 53% 93%, rgba(255, 69, 0, 0.16) 0 1px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 64% 82%, rgba(255, 69, 0, 0.27) 0 2px, rgba(0,0,0,0) 5px),
                radial-gradient(circle at 78% 94%, rgba(255, 69, 0, 0.20) 0 1px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 90% 83%, rgba(255, 69, 0, 0.26) 0 2px, rgba(0,0,0,0) 5px);
            animation: sparks-layer-a 5.5s ease-in-out infinite alternate;
        }}

        body::after {{
            content: "";
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            height: 12dvh;
            pointer-events: none;
            z-index: 2;
            opacity: 0.55;
            filter: blur(0.4px);
            background:
                radial-gradient(circle at 6% 85%, rgba(255, 69, 0, 0.35) 0 2px, rgba(0,0,0,0) 3px),
                radial-gradient(circle at 14% 90%, rgba(255, 69, 0, 0.28) 0 1px, rgba(0,0,0,0) 3px),
                radial-gradient(circle at 22% 78%, rgba(255, 69, 0, 0.40) 0 2px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 31% 92%, rgba(255, 69, 0, 0.22) 0 1px, rgba(0,0,0,0) 3px),
                radial-gradient(circle at 43% 80%, rgba(255, 69, 0, 0.32) 0 2px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 55% 95%, rgba(255, 69, 0, 0.18) 0 1px, rgba(0,0,0,0) 3px),
                radial-gradient(circle at 66% 82%, rgba(255, 69, 0, 0.36) 0 2px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 77% 90%, rgba(255, 69, 0, 0.24) 0 1px, rgba(0,0,0,0) 3px),
                radial-gradient(circle at 88% 79%, rgba(255, 69, 0, 0.38) 0 2px, rgba(0,0,0,0) 4px),
                radial-gradient(circle at 95% 93%, rgba(255, 69, 0, 0.20) 0 1px, rgba(0,0,0,0) 3px);
            animation: sparks-layer-b 3.6s ease-in-out infinite alternate;
        }}

        @keyframes sparks-layer-a {{
            0% {{ transform: translate(0, 0) scale(1); opacity: 0.28; }}
            50% {{ transform: translate(10px, -6px) scale(1.02); opacity: 0.42; }}
            100% {{ transform: translate(-8px, -10px) scale(1.01); opacity: 0.34; }}
        }}

        @keyframes sparks-layer-b {{
            0% {{ transform: translate(0, 0) scale(1); opacity: 0.45; }}
            35% {{ transform: translate(-12px, -6px) scale(1.03); opacity: 0.62; }}
            70% {{ transform: translate(14px, -12px) scale(1.01); opacity: 0.52; }}
            100% {{ transform: translate(-6px, -16px) scale(1.02); opacity: 0.66; }}
        }}
        
        .top-header {{ height: 18dvh; display: flex; flex-direction: column; justify-content: center; align-items: center; border-bottom: 1px solid #111; position: relative; }}
        .header-title {{ font-size: 5.5vh; letter-spacing: 20px; font-weight: 200; text-transform: uppercase; }}

        /* Üstteki DJ etiketi (pembe + küçük animasyon) */
        #dj-top {{
            position: absolute;
            left: 46px; /* biraz sağa al */
            top: 6px; /* saat ile aynı yükseklik */
            z-index: 5;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-top: 0;
            color: #ff4fd6; /* pembe */
            font-weight: 900;
            letter-spacing: 4px;
            text-transform: uppercase;
            font-size: 1.05vh;
            opacity: 0.95;
            animation: dj-breathe 1.8s ease-in-out infinite alternate;
            white-space: nowrap;
            flex-direction: column; /* ikon üstte, isim altta */
        }}
        #dj-top .dj-label {{ color: #ff4fd6; }}
        #dj-top .dj-name {{ color: #ffae00; }}
        #dj-top img {{
            /* DJ/GIF görseli daha büyük */
            width: clamp(120px, 14vh, 220px);
            height: clamp(120px, 14vh, 220px);
            flex: 0 0 auto;
            color: #fff; /* DJ ikonu siyah-beyaz */
            object-fit: contain;
            filter: grayscale(1) brightness(1.55) contrast(1.15);
            opacity: 0.98;
            will-change: transform;
            animation: dj-img-move 1.1s ease-in-out infinite;
            background: transparent; /* arka plan/kutu olmasın */
            border: none; /* arka plan/kutu olmasın */
            border-radius: 0; /* arka plan/kutu olmasın */
            padding: 0; /* arka plan/kutu olmasın */
        }}

        /* Link ile gelen DJ görsellerinde filtre uygulama */
        #dj-top img.dj-custom {{
            filter: none;
        }}

        /* (eski özel DJ img id'leri kaldırıldı) */
        @keyframes dj-img-move {{
            0% {{ transform: translateY(0px) rotate(-2deg) scale(1.00); }}
            50% {{ transform: translateY(-6px) rotate(2deg) scale(1.02); }}
            100% {{ transform: translateY(0px) rotate(-2deg) scale(1.00); }}
        }}
        #dj-top.dj-top-pop {{
            animation: dj-pop 520ms ease-in-out 1;
        }}
        @keyframes dj-breathe {{
            from {{ transform: translateY(0px); opacity: 0.70; }}
            to {{ transform: translateY(-2px); opacity: 1; }}
        }}
        @keyframes dj-pop {{
            0% {{ transform: scale(0.98) translateY(0px); opacity: 0.75; }}
            60% {{ transform: scale(1.02) translateY(-1px); opacity: 1; }}
            100% {{ transform: scale(1.00) translateY(0px); opacity: 0.95; }}
        }}
        
        /* NEWROZ YAZISI - BİR ALTTA VE YAVAŞ */
        #newroz-sub {{ font-size: 1.8vh; color: #ff0000; letter-spacing: 8px; margin-top: 25px; font-weight: bold; animation: slow-flash 4s infinite; }}
        
        /* SABİT DİNLEYİCİ SAYISI - SAĞ ÜST (GIF ile hizalı) */
        .live-stats {{
            position: absolute;
            right: 40px;
            top: 6px;
            /* GIF büyüyünce görsel merkez hizası için biraz aşağı al */
            transform: translateY(18px);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        .analog-clock {{ width: 78px; height: 78px; filter: drop-shadow(0 0 6px rgba(255,255,255,0.10)); }}
        .analog-clock canvas {{ width: 78px; height: 78px; display: block; }}
        .viewer-line {{ display: flex; align-items: center; gap: 10px; }}
        .live-circle {{ width: 8px; height: 8px; background: #00ff00; border-radius: 50%; }}
        .viewer-text {{ color: rgba(0, 255, 0, 0.4); font-size: 1.2vh; font-weight: bold; letter-spacing: 2px; }}

        .main-grid {{ display: flex; height: 82dvh; width: 100%; position: relative; z-index: 1; }}
        .panel {{ padding: 2vh; display: flex; flex-direction: column; background: #000; height: 100%; }}
        .col-flow {{ flex: 20; border-right: 1px solid #111; overflow: hidden; display: flex; flex-direction: column; }}
        .col-player {{ flex: 60; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .col-chat {{
            flex: 20;
            border-left: 1px solid #111;
            background: #050505;
            position: relative;
            overflow: hidden;
        }}
        /* Chat arka planına yumuşak, blur'lı animasyon */
        .col-chat::before {{
            content: "";
            position: absolute;
            inset: -60px;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 20% 20%, rgba(255, 69, 0, 0.18), rgba(0,0,0,0) 55%),
                radial-gradient(circle at 75% 55%, rgba(0, 255, 120, 0.10), rgba(0,0,0,0) 55%),
                radial-gradient(circle at 40% 90%, rgba(255, 255, 255, 0.05), rgba(0,0,0,0) 60%);
            filter: blur(16px);
            opacity: 0.9;
            animation: chatBgShift 7s ease-in-out infinite alternate;
        }}
        .col-chat > * {{
            position: relative;
            z-index: 1;
        }}
        @keyframes chatBgShift {{
            0% {{ transform: translate(0px, 0px) scale(1.02); opacity: 0.75; }}
            50% {{ transform: translate(10px, -8px) scale(1.04); opacity: 0.95; }}
            100% {{ transform: translate(-8px, 6px) scale(1.03); opacity: 0.85; }}
        }}

        .flow-title {{
            padding: 1.1vh 1vh 0.8vh 1vh;
            color: #ff4500;
            font-weight: 900;
            letter-spacing: 6px;
            text-transform: uppercase;
            font-size: 1.5vh;
            border-bottom: 1px solid #111;
            margin-bottom: 1.2vh;
            opacity: 0.95;
            white-space: nowrap;
        }}

        /* Chat UI (scoped to chat column) */
        .col-chat {{ display: flex; flex-direction: column; }}
        .col-chat .chat-wrap {{ display: flex; flex-direction: column; flex: 1; min-height: 0; margin-top: 1.2vh; gap: 1vh; }}
        .col-chat .chat-log {{
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            overscroll-behavior: contain;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 1.2vh;
            background: linear-gradient(180deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
            box-shadow: inset 0 0 0 1px rgba(0,0,0,0.45);
        }}
        .chat-pinned {{
            padding: 0.9vh 1vh;
            border-radius: 12px;
            margin-bottom: 0.9vh;
            background: rgba(255, 69, 0, 0.12);
            border: 1px solid rgba(255, 69, 0, 0.22);
            color: rgba(255,255,255,0.92);
            font-size: clamp(12px, 1.15vh, 14px);
            font-weight: 700;
            letter-spacing: 0.2px;
        }}
        .col-chat .chat-log::-webkit-scrollbar {{ width: 8px; }}
        .col-chat .chat-log::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.03); border-radius: 999px; }}
        .col-chat .chat-log::-webkit-scrollbar-thumb {{ background: rgba(255,69,0,0.28); border-radius: 999px; }}

        .col-chat .chat-msg {{
            font-size: clamp(12px, 1.15vh, 14px);
            color: rgba(255,255,255,0.88);
            line-height: 1.35;
            margin-bottom: 0.9vh;
            word-break: break-word;
            padding: 0.9vh 1vh;
            border-radius: 12px;
            background: rgba(0,0,0,0.22);
            border: 1px solid rgba(255,255,255,0.055);
            animation: msgIn 420ms ease-out both;
        }}
        @keyframes msgIn {{
            from {{ opacity: 0; transform: translateY(6px) scale(0.995); }}
            to {{ opacity: 1; transform: translateY(0px) scale(1); }}
        }}
        .col-chat .chat-msg:last-child {{ margin-bottom: 0; }}
        .col-chat .chat-meta {{
            font-size: clamp(10px, 0.95vh, 12px);
            color: rgba(255,255,255,0.50);
            letter-spacing: 0.4px;
            margin-bottom: 0.35vh;
        }}
        .chat-name-active {{ color: rgba(0, 255, 120, 0.85); font-weight: 750; }}
        .chat-name-inactive {{ color: rgba(255, 100, 100, 0.85); font-weight: 750; }}
        .chat-time {{ color: rgba(255,255,255,0.52); font-weight: 600; }}
        .col-chat .chat-input {{ display: flex; gap: 0.8vh; align-items: center; }}
        .col-chat #chatName, .col-chat #chatText {{
            flex: 1;
            background: rgba(0,0,0,0.40);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 12px;
            padding: 1vh 1.1vh;
            font-size: clamp(12px, 1.1vh, 14px);
            outline: none;
            min-width: 0; /* flex'te taşmayı engeller (butonu saga kaydiran durum) */
        }}
        .col-chat #chatName {{ flex: 0.65; }}
        .col-chat #chatName:focus, .col-chat #chatText:focus {{
            border-color: rgba(255,69,0,0.55);
            box-shadow: 0 0 0 3px rgba(255,69,0,0.12);
        }}
        .col-chat #chatSend {{
            background: rgba(255,69,0,0.14);
            color: #fff;
            border: 1px solid rgba(255,69,0,0.40);
            border-radius: 12px;
            padding: 1vh 1.1vh;
            font-size: clamp(12px, 1.05vh, 14px);
            cursor: pointer;
            white-space: nowrap;
            transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
            flex: 0 0 auto;
        }}
        .col-chat #chatSend:hover {{ background: rgba(255,69,0,0.22); border-color: rgba(255,69,0,0.55); }}
        .col-chat #chatSend:active {{ transform: translateY(1px); }}
        .col-chat #chatSend:disabled {{ opacity: 0.55; cursor: not-allowed; }}
        .col-chat #chatStatus {{ margin-top: 0.2vh; font-size: clamp(10px, 1.0vh, 12px); color: rgba(255,255,255,0.50); }}

        /* Sohbet içi admin (anlık DJ) satırı */
        .col-chat #chatAdminLine {{
            text-align: center;
            color: rgba(255, 255, 255, 0.86);
            font-size: clamp(11px, 1.15vh, 13px);
            letter-spacing: 2px;
            margin-top: 0.7vh;
            margin-bottom: 0.2vh;
            padding: 0.65vh 0.8vh;
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.03);
            user-select: none;
        }}
        .col-chat #chatAdminLine .admin-label {{ color: #ff4500; font-weight: 900; }}
        .col-chat #chatAdminLine .admin-name {{ color: #ffffff; font-weight: 800; }}
        .col-chat #chatAdminLine .admin-active {{ color: rgba(0,255,0,0.70); font-weight: 900; }}
        
        /* Yayın akışı: kaydırmasız, 1 ekrana sığsın */
        .row-item {{ flex: 1 1 0; min-height: 0; padding: 0.95vh 1vh; border-bottom: 1px solid rgba(255,255,255,0.06); opacity: 0.38; }}
        .row-item > div:first-child {{ color: rgba(255,255,255,0.72); letter-spacing: 0.5px; }}
        .row-item > div:nth-child(2) {{ color: rgba(255, 110, 60, 0.92) !important; }}
        .active {{ opacity: 1; border-left: 5px solid #ff4500; background: rgba(255, 69, 0, 0.09); box-shadow: inset 0 0 0 1px rgba(255, 69, 0, 0.12), 0 0 18px rgba(255, 69, 0, 0.08); }}
        .row-desc {{ font-size: 1.05vh; color: rgba(255,255,255,0.70); margin-top: 0.25vh; }}
        .dj-inline {{
            color: rgba(255,255,255,0.52);
            font-weight: 700;
            letter-spacing: 0.8px;
            font-size: 0.72em;
            opacity: 0.85;
        }}
        
        .disk-wrapper {{ width: 40vh; height: 40vh; border-radius: 50%; border: 15px solid #111; overflow: hidden; background: #000; animation: rotate-disk 40s linear infinite; }}
        @keyframes rotate-disk {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
        .disk-img {{ width: 100%; height: 100%; object-fit: contain; }}
        
        #display-song-name {{ font-size: 2vh; font-weight: 300; letter-spacing: 4px; margin-top: 5vh; text-align: center; text-transform: uppercase; }}
        #display-category-name {{ color:#ff4500; font-size:1.2vh; letter-spacing:7px; margin-top:1.5vh; font-weight: bold; }}
        /* DJ artık üstte gösterilecek; alttaki tekrar görünmesin */
        #display-dj-name, #display-dj-note {{ display: none; }}
        
        @keyframes slow-flash {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.2; }} }}
        
        #control-button {{ margin-top: 4vh; padding: 1.5vh 8vh; font-size: 1vh; font-weight: bold; background: transparent; color: #fff; border: 1px solid #333; border-radius: 50px; cursor: pointer; }}

        /* ---------------- Mobil düzen (JS class ile) ---------------- */
        html.mobile-layout, body.mobile-layout {{
            overflow-y: hidden; /* panel içleri scroll olacak */
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            height: 100dvh;
        }}
        html.mobile-layout .top-header, body.mobile-layout .top-header {{
            height: 20dvh;
        }}
        html.mobile-layout .header-title, body.mobile-layout .header-title {{
            font-size: clamp(24px, 6.5vw, 40px);
            letter-spacing: 10px;
        }}
        html.mobile-layout .live-stats, body.mobile-layout .live-stats {{
            position: absolute;
            right: 14px;
            top: 6px; /* DJ ile aynı yükseklik */
            margin-top: 0;
            gap: 6px;
            transform: translateY(16px);
        }}
        html.mobile-layout .analog-clock {{ width: 60px; height: 60px; }}
        html.mobile-layout .analog-clock canvas {{ width: 60px; height: 60px; }}
        html.mobile-layout .viewer-text {{ font-size: 1.0vh; }}
        html.mobile-layout #newroz-sub, body.mobile-layout #newroz-sub {{
            font-size: clamp(12px, 2.1vh, 18px);
            letter-spacing: 5px;
            margin-top: 12px;
        }}
        html.mobile-layout #dj-top img, body.mobile-layout #dj-top img {{
            width: clamp(110px, 13vh, 200px);
            height: clamp(110px, 13vh, 200px);
        }}
        html.mobile-layout .viewer-text, body.mobile-layout .viewer-text {{
            font-size: 1.0vh;
            letter-spacing: 1.5px;
        }}

        html.mobile-layout .main-grid, body.mobile-layout .main-grid {{
            flex-direction: column;
            height: calc(100dvh - 20dvh);
            min-height: 0; /* flex için */
            flex: 1 1 auto;
        }}
        html.mobile-layout .panel, body.mobile-layout .panel {{
            padding: 1.2dvh;
            height: auto;
            min-height: 0; /* içerik taşınca binmeyi engeller */
        }}
        html.mobile-layout .col-flow, body.mobile-layout .col-flow {{
            display: none; /* mobilde yayın akışı kalksın */
        }}
        html.mobile-layout .col-player, body.mobile-layout .col-player {{
            flex: 0 0 18dvh;
            max-height: 18dvh;
        }}
        html.mobile-layout .col-chat, body.mobile-layout .col-chat {{
            flex: 1 1 auto; /* kalan yükseklik */
            border-left: none;
            border-top: 1px solid #111;
            max-height: none;
            min-height: 0;
        }}

        html.mobile-layout .disk-wrapper, body.mobile-layout .disk-wrapper {{
            width: clamp(100px, 32vw, 160px);
            height: clamp(100px, 32vw, 160px);
            border: 6px solid #111;
            display: none; /* mobilde görseli görünmez yap */
        }}
        html.mobile-layout #display-song-name, body.mobile-layout #display-song-name {{
            font-size: clamp(15px, 3.0vh, 20px);
            margin-top: 0.6dvh;
            letter-spacing: 3px;
        }}
        html.mobile-layout #display-category-name, body.mobile-layout #display-category-name {{
            display: block; /* program başlığı tekrar görünsün */
            color: #ff4500;
            font-size: clamp(12px, 2.1vh, 16px);
            letter-spacing: 4px;
            margin-top: 0.3dvh;
            font-weight: 900;
        }}
        html.mobile-layout #display-dj-name, body.mobile-layout #display-dj-name {{
            margin-top: 0.6dvh;
            font-size: clamp(12px, 2.1vh, 16px);
            letter-spacing: 3px;
        }}
        html.mobile-layout #display-dj-note, body.mobile-layout #display-dj-note {{
            margin-top: 0.2dvh;
            font-size: clamp(10px, 1.7vh, 13px);
        }}
        html.mobile-layout #control-button, body.mobile-layout #control-button {{
            margin-top: 0.5dvh;
            padding: 12px 22px;
            font-size: 13px;
            border-radius: 999px;
        }}
        html.mobile-layout .row-item, body.mobile-layout .row-item {{
            padding: 0.45dvh 0.7vh;
            flex: 0 0 auto; /* mobilde satırların eşit dağıtılmasını durdur; kartlar kendi yüksekliğini alsın */
            min-height: auto;
        }}
        html.mobile-layout .col-flow .row-item, body.mobile-layout .col-flow .row-item {{
            overflow: hidden;
        }}
        html.mobile-layout .row-desc, body.mobile-layout .row-desc {{
            font-size: clamp(12px, 1.9vh, 14px);
        }}
        /* Akış tek satır: her kart eşit genişlik alsın, alt çizgi kalksın */
        html.mobile-layout .col-flow .row-item, body.mobile-layout .col-flow .row-item {{
            flex: 1 1 0;
            border-bottom: none;
            padding: 0 0.6vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        /* Akışta sadece başlık kalsın (scroll yok, tek satır) */
        html.mobile-layout .col-flow .row-item > div:first-child {{
            display: none; /* zaman yazısını gizle */
        }}
        html.mobile-layout .col-flow .row-item > div:nth-child(2) {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: clamp(10px, 1.6vh, 13px);
            line-height: 1.1;
            letter-spacing: 0.2px;
            max-width: 100%;
        }}
        /* Aktif durum çizgisini yataya uyarlayalım */
        html.mobile-layout .row-item.active {{
            border-left: none;
            border-bottom: 3px solid #ff4500;
            background: rgba(255, 69, 0, 0.09);
        }}
        html.mobile-layout .col-flow .row-desc, body.mobile-layout .col-flow .row-desc {{
            display: none; /* mobilde akış kartları arası boşluk çok genişliyor, açıklamayı kaldırıyoruz */
        }}
        html.mobile-layout .col-flow .row-item > div:first-child {{
            font-size: 12px;
            white-space: nowrap;
        }}
        html.mobile-layout .col-flow .row-item > div:nth-child(2) {{
            font-size: 14px;
            line-height: 1.15;
        }}

        html.tiny-layout .col-chat .chat-input, body.tiny-layout .col-chat .chat-input {{
            flex-direction: column;
        }}
        html.tiny-layout #chatName, body.tiny-layout #chatName {{
            flex: 0 0 auto;
            width: 100%;
        }}
        html.tiny-layout #chatText, body.tiny-layout #chatText {{
            width: 100%;
        }}
        html.tiny-layout #chatSend, body.tiny-layout #chatSend {{
            width: 100%;
        }}

        /* Mobilde sohbeti büyüt (okunur olsun) */
        html.mobile-layout .col-chat .chat-log {{
            padding: 1.4dvh;
            border-radius: 16px;
        }}
        html.mobile-layout .col-chat .chat-msg {{
            font-size: clamp(13px, 1.5vh, 16px);
            padding: 1.0dvh 1.1vh;
            line-height: 1.35;
        }}
        html.mobile-layout .col-chat #chatName, body.mobile-layout .col-chat #chatName,
        html.mobile-layout .col-chat #chatText, body.mobile-layout .col-chat #chatText {{
            font-size: clamp(13px, 1.4vh, 16px);
            padding: 1.1dvh 1.15vh;
        }}
        html.mobile-layout .col-chat #chatSend {{
            font-size: clamp(13px, 1.3vh, 16px);
            padding: 1.1dvh 1.25vh;
        }}

    </style>
    <script src="https://cdn.ably.com/lib/ably.min-1.js" defer></script>
</head>
<body>
<script>
    (function () {{
        function apply() {{
            const w = window.innerWidth || 0;
            const isMobile = w <= 1024;
            const isTiny = w <= 420;
            document.documentElement.classList.toggle('mobile-layout', isMobile);
            document.body.classList.toggle('mobile-layout', isMobile);
            document.documentElement.classList.toggle('tiny-layout', isTiny);
            document.body.classList.toggle('tiny-layout', isTiny);
        }}
        apply();
        window.addEventListener('resize', apply);
    }})();
</script>
<div class="top-header">
    <div class="header-title">HALKLARIN SESİ RADYOSU</div>
    <div id="newroz-sub">NEWROZ PÎROZ BE!</div>
    <div id="dj-top">
        <!-- DJ animasyon görseli (siyah-beyaz, CSS ile hareket) -->
        <img
            id="dj-top-img"
            alt="DJ"
            draggable="false"
            loading="eager"
            decoding="async"
            style="display:none;"
            src=""
        />
        <span id="dj-top-text">DJ: --</span>
    </div>
    <div class="live-stats">
        <div class="analog-clock">
            <canvas id="analogClock" width="78" height="78"></canvas>
        </div>
        <div class="viewer-line">
            <div class="live-circle"></div>
            <div class="viewer-text">CANLI: <span id="viewers">12</span> DİNLEYİCİ</div>
        </div>
    </div>
</div>
<div class="main-grid">
    <div class="panel col-flow">
        <div class="flow-title">YAYIN AKIŞI</div>
        <div class="row-item" data-key="ahmet_kaya" data-start="0" data-end="3">
            <div>00:00 — 03:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="ahmet_kaya">AHMET KAYA ŞARKILARI</div>
            <div class="row-desc">Sürgünün, özlemin ve isyanın sesi Ahmet Kaya'nın sevilen şarkıları.</div>
        </div>
        <div class="row-item" data-key="ermeni_ezgileri" data-start="3" data-end="6">
            <div>03:00 — 06:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="ermeni_ezgileri"> ERMENİ HALK EZGİLERİ</div>
            <div class="row-desc">Ermenice şarkı seçkileri.</div>
        </div>
        <div class="row-item" data-key="mozaik" data-start="6" data-end="11">
            <div>06:00 — 11:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="mozaik">MOZAİK</div>
            <div class="row-desc">Farklı dillerden, kültürlerden özgürlük ezgileri.</div>
        </div>
        <div class="row-item" data-key="tsm" data-start="11" data-end="14">
            <div>11:00 — 14:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="tsm">TSM SAATİ</div>
            <div class="row-desc">Klasik Türk sanat müziğiyle nostaljik bir yolculuk.</div>
        </div>
        <div class="row-item" data-key="tiyatro" data-start="14" data-end="17">
            <div>14:00 — 17:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="tiyatro">RADYO TİYATROSU</div>
            <div class="row-desc">Toplumsal gerçekçi oyunlar ve sesli hikâyeler.</div>
        </div>
        <div class="row-item" data-key="soldan_sesler" data-start="17" data-end="20">
            <div>17:00 — 20:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="soldan_sesler">SOLDAN SESLER</div>
            <div class="row-desc">Politik ve alternatif şarkı seçkileri.</div>
        </div>
        <div class="row-item" data-key="tasavvuf" data-start="20" data-end="21">
            <div>20:00 — 21:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="tasavvuf">TASAVVUF VAKTİ</div>
            <div class="row-desc">Tasavvuf musikisi ve mistik ezgiler.</div>
        </div>
        <div class="row-item" data-key="anadolu_rock" data-start="21" data-end="22">
            <div>21:00 — 22:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="anadolu_rock">ANADOLU ROCK</div>
            <div class="row-desc">Anadolu rock’ın efsaneleşmiş şarkıları.</div>
        </div>
        <div class="row-item" data-key="grup_yorum" data-start="22" data-end="24">
            <div>22:00 — 00:00</div>
            <div style="font-weight:bold; color:#ff4500;" data-title-for="grup_yorum">GRUP YORUM SAATİ</div>
            <div class="row-desc">Direnişin sesi Grup Yorum’dan seçilmiş eserler.</div>
        </div>
    </div>
    <div class="panel col-player">
        <div class="disk-wrapper"><img id="main-disk-img" class="disk-img" src=""></div>
        <div id="display-song-name">BAĞLANILIYOR...</div>
        <div id="display-category-name">MASTER YAYIN</div>
        <div id="display-dj-name">DJ AHMET</div>
        <div id="display-dj-note">Canlı yayın ekibi • DJ Bilgi</div>
        <button id="control-button">YAYINI BAŞLAT</button>
    </div>
    <div class="panel col-chat">
        <div style="text-align:center; color:#ff4500; font-size:1.1vh; font-weight:bold; letter-spacing:4px;">CANLI SOHBET</div>
        <div id="chatAdminLine"><span class="admin-label">ADMIN:</span> <span class="admin-name">--</span> <span class="admin-active">(aktif)</span></div>
        <div class="chat-wrap">
            <div id="chatPinned" class="chat-pinned"></div>
            <div id="chatLog" class="chat-log"></div>
            <div class="chat-input">
                <input id="chatName" placeholder="İsim" maxlength="24" />
                <input id="chatText" placeholder="Mesaj yaz..." maxlength="240" />
                <button id="chatSend">GÖNDER</button>
            </div>
            <div id="chatStatus"></div>
        </div>
    </div>
</div>

<script>
    const radioData = {data_json};

    // --- ABLY CHAT ---
    (function initChat() {{
        const logEl = document.getElementById('chatLog');
        const nameEl = document.getElementById('chatName');
        const textEl = document.getElementById('chatText');
        const sendEl = document.getElementById('chatSend');
        const statusEl = document.getElementById('chatStatus');
        const adminLineEl = document.getElementById('chatAdminLine');
        const pinnedEl = document.getElementById('chatPinned');

        try {{
        // Presence'a göre aktiflik rengi:
        // Ably tarafında sohbet sayfası açık olanlar presence "enter" olur, kapanınca "leave" gelir.
        const memberIdToName = {{}};
        const activeNameCount = {{}};

        const normalizeName = (n) => {{
            const s = (n || '').toString().trim();
            return s || 'Anonim';
        }};

        const adjustActive = (name, delta) => {{
            const nn = normalizeName(name);
            activeNameCount[nn] = (activeNameCount[nn] || 0) + delta;
            if (activeNameCount[nn] <= 0) delete activeNameCount[nn];
        }};

        // Basit küfür + spam engelleyici (client-side).
        // Not: Bu filtreler kesin güvenlik sağlamaz (bypass edilebilir),
        // ama normal kullanıcılar için büyük ölçüde engeller.
        const normalizeForFilter = (s) => {{
            try {{
                const t = (s === null || s === undefined) ? '' : String(s);
                return t
                    .toLowerCase()
                    .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '') // Türkçe karakter sadeleştir
                    .replace(/[^a-z0-9\\s]/g, ' ') // noktalama vb. ayikla
                    .replace(/\\s+/g, ' ')
                    .trim()
                    // mükerrer harfleri biraz azalt: 'siiiiik' -> 'siiik' gibi
                    .replace(/([a-z0-9])\\1{{2,}}/g, '$1$1');
            }} catch (e) {{
                return String(s || '');
            }}
        }};

        // Küfür/argo engeli kelimeleri.
        // Not: Bu filtreler client-side olduğu için %100 güvenlik değil; ama pratikte çoğu mesajı engeller.
        const bannedWordsRaw = `
amk
orospu
sik
yarrak
göt
got
amcik
serefsiz
siktir
anan
ananı
ananin
pic
sikeyim
sikerim
sikiyim
sikmek
ibne
agzina veririm
agzini yuzunu sikerim
allah belani versin
allah cezani versin
allahini
am biti
ambiti
amcik
amimi
amimizi
amina
amina koyarim
amini
amini sikerim
aminizi
anani
anan avradini
avradini
avag
arsiz
asil
aşağılık
asil
asagilik
asagilik kadin
ateşin başına vurdu
atesin basina vurdu
avrat
avradini
ayağa düşürürüm
ayaga dusururum
azgin
bacaklarini kirarim
bacini
beyinsiz
bogazini kesecem
bogazini
bok
cahil
camis
camiz
cerceveni dagitirim
cirkin
curuk kadin
curumussun
daga kaldiririm
dancuk
dang
dal
davar
deli
dillerim
dingil
dinsiz
domuz
dumbugun kizi
dumbuk
eksik etek
elinde kalirsin
essolesek
etigine ettigimin karisi
eteğine ettiğimin karısı
etigine ettigimin karisi
façanı aşağı alırım
facani asagi alirim
fahise
fettan
gavur
gavurun dolu
geber
genelev
genelev kadini
genelevlere dusesin
geri zekali
gerizekali
gogus
gorgusuz
got oglani
gotoglani
got deligini
gotdeligini
gotume
gotumu
gotumuzu
gotune
gotunu
gotunu keserim
gotunu sikerim
gotunuzu
götünden sikerim
hayvan
hiyar
kahpe
kaltak
kancik
kani bozuk
karnini deşerim
karnini deserim
kavatin kizi
kiz
kic
kimden peydahladin
kizismis
komaya sokarim
kopek
malafat
mamis
mankafa
manyak
mezarina tukurmem
mikrop
o.c
oç
oc
okuz
oro
orospu cocugu
oro.?
oç
o.ç.
Orospu cocugu
p.k.k
PKK
DHKPC
pandik
pavyon karisi
pavyona mi dusecen
pezevenk
pic
piç
pipi
pisirik
pislik
popo
psikopat
pust
 sacakli
sakal
sapik
serefsiz
seyin basina vurdu
sicar
sicarsin
sicariz
sicarlar
sicmak
sik kafali
siker
sikerim
sikeriz
sikerler
sikersin
sikersiniz
sikilmis
sikimi
sikis
sikisgen
sikismek
sikmek
siktigim
siktim
siktir
sirfinti
sirret
sokak surtugu
sokarim
soktum
soysuz
slaleni
supruntu
surtuk
sutu bozuk
travesti
ulan
ulan kari
uyuz
vajina
Ya cik git ya intihar et
yakalarsam seni satacam
yalaka
yalama
yal arim
yamuk kadin
yavsak
yer cucesi
yeteneksiz
yosma
sik kafali
amın oğlu
aminoğlu
sikko
at yarrağı
yarrak kafalı
yarrak ye
yarrak surat
sik kafa
am biti
suratını sikeyim
sikiyim
anan
a.k
a.q
abaza
abazan
amcik
agzini yuzunu sikerim
Allah belani versin
Allah cezani versin
Piç
Puşt
Puşt
Pezevenk
serefsiz
Sokarım
şerefsiz
şeyin başına vurdu
Sıçar
Sıçmak
Sikiş
Sikişgen
Sikişmek
Siktir
şapşal
şırfıntı
şirret
Sokak sürtüğü
Soysuz
Sülaleni
Sümüklü
Süprüntü
Sürtük
Sütü Bozuk
Kürt
KKK
eşek
eşşek
eşşeoğlueşşek
eşekoğlueşek
ok
siktir
`;

        // Performans: Çok büyük bir listeyi burada parçalayarak normalize etmek
        // sayfa yüklemesini ciddi yavaşlatıyor.
        // Bu yüzden ana filtreleme, alttaki bannedStemsRaw/bannedPhrasesRaw ile yapılıyor.
        const bannedWords = [];
        const bannedWordsNorm = [];

        const sexualWords = [
            // Açık içerik yerine daha genel NSFW/erotik çağrışımlar (graphic kelimeler eklemeden)
            'seks',
            'sex',
            'porno',
            'porn',
            'pornografi',
            'erotik',
            'cinsel',
            'cinsellik',
            'fetiş',
            'fetis',
            'nsfw',
            'xxx',
            'anal',
            'porno',
            'penis',
            'dildo',
            'pussy',
            'pipi',
            'vajina',
            'oral',
            'sperm',
            'sakso',
            'masturbasyon',
            'sevis',
            'seviş',
            'seviselim',
        ];

        // Listeyi tek tek eklemek çok uzun olacağı için,
        // normalize edilmiş metinde yakalamaya yarayan "kök/desen" kontrolleri.
        const bannedStemsRaw = [
            'abaza',
            'abazan',
            'allah belani',
            'allah cezani',
            'amcik',
            'amc',
            'ambiti',
            'amck',
            'amik',
            'amimi',
            'amimizin',
            'amını',
            'amına',
            'amında',
            'amsalak',
            'dalyarak',
            'dasak',
            'dassak',
            'dassagi',
            'dasagi',
            'domalam',
            'cük',
            'dol',
            'meme',
            'oc',
            'aq',
            'aqq',
            'oral',
            'am biti',
            'orospu',
            'orosbu',
            'orsp',
            'orospu cocugu',
            'pezevenk',
            'puşt',
            'pust',
            'ibne',
            'ipne',
            'kaltak',
            'kaltag',
            'kahpe',
            'kancik',
            'kancig',
            'serefsiz',
            'salak',
            'gerizekali',
            'aptal',
            'travesti',
            'yarrak',
            'yaraq',
            'yrrk',
            'yavsak',
            'yarrami',
            'göt',
            'got',
            'godo',
            'godoş',
            'gavat',
            'pic',
            'sik',
            'sikis',
            'sikisgen',
            'sikici',
            'sikik',
            'sikmek',
            'siktir',
            'sktr',
            'hasiktir',
            'hassiktir',
            'surtuk',
            'taşak',
            'taskak',
            'tasak',
            'tassak',
            'tasagi',
            'tasaga',
            'yalaka',
            'vagina',
            'vajina',
            'fahise',
            'follos',
            'fahişe',
            'follos',
            'kerane',
            'kerhane',
            'kevase',
            'kavat',
            'qavat',
            'puşt',
            'puştt',
            'vajina',
        ];

        const bannedPhrasesRaw = [
            'agzina veririm',
            'agzini yuzunu sikerim',
            'agzina sıcarım',
            'allah belani versin',
            'allah cezani versin',
            'sik kafali',
            'yarrak kafali',
        ];

        const bannedStemsNorm = bannedStemsRaw.map(normalizeForFilter).filter(Boolean);
        const bannedPhrasesNorm = bannedPhrasesRaw.map(normalizeForFilter).filter(Boolean);

        // txt'den gelen kelimeler Python tarafında normalize edilmiş "compact" stringler.
        const bannedStemsFromTxt = (radioData && radioData.bannedStemsFromTxt) ? radioData.bannedStemsFromTxt : [];
        const bannedStemsAll = Array.from(new Set([...(bannedStemsNorm || []), ...(bannedStemsFromTxt || [])]));

        const bannedPhrasesCompact = (bannedPhrasesNorm || []).map(ph => String(ph || '').replace(/\s+/g, '')).filter(ph => ph.length >= 3);

        const isProfane = (text) => {{
            return false;
        }};

        const isSexual = (text) => {{
            return false;
        }};

        let myLastSendAt = 0;
        let mySendTimes = []; // son 60 saniyedeki gönderimler
        let myLastNormText = '';
        let myRepeatCount = 0;

        const updateActiveColors = () => {{
            if (!logEl) return;
            const nameEls = logEl.querySelectorAll('.chat-name[data-name]');
            nameEls.forEach(el => {{
                const n = el.getAttribute('data-name') || '';
                const isActive = !!activeNameCount[normalizeName(n)];
                el.classList.toggle('chat-name-active', isActive);
                el.classList.toggle('chat-name-inactive', !isActive);
            }});
        }};

        const pushMsg = (name, text) => {{
            if (!logEl) return;
            const displayName = normalizeName(name);
            const wrap = document.createElement('div');
            wrap.className = 'chat-msg';
            const meta = document.createElement('div');
            meta.className = 'chat-meta';
            const nameSpan = document.createElement('span');
            nameSpan.className = 'chat-name';
            nameSpan.setAttribute('data-name', displayName);
            nameSpan.textContent = displayName;

            // Presence durumuna göre renk
            nameSpan.classList.add(activeNameCount[displayName] ? 'chat-name-active' : 'chat-name-inactive');

            const timeSpan = document.createElement('span');
            timeSpan.className = 'chat-time';
            timeSpan.textContent = ' • ' + new Date().toLocaleTimeString();

            meta.appendChild(nameSpan);
            meta.appendChild(timeSpan);
            const body = document.createElement('div');
            body.textContent = text || '';
            wrap.appendChild(meta);
            wrap.appendChild(body);
            logEl.appendChild(wrap);
            while (logEl.children.length > 40) logEl.removeChild(logEl.firstChild);
            logEl.scrollTop = logEl.scrollHeight;

            updateActiveColors();
        }};

        const normalizeDjKeyForPinned = (s) => {{
            const t = (s || '').toString().trim().toLowerCase();
            // Türkçe karakterleri sadeleştir + boşluk/altçizgi/çizgi temizle
            return t
                .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
                .replace(/\\s+/g, '')
                .replace(/[_-]+/g, '_');
        }};

        const updatePinnedForDj = (djText) => {{
            if (!pinnedEl) return;
            const djName = normalizeDjKeyForPinned(
                (djText || '').toString().replace(/^DJ\\s*/i, '')
            );
            const msgMap = (radioData && radioData.pinnedDjMessages) ? radioData.pinnedDjMessages : {{}};
            const msg = (djName && msgMap && msgMap[djName]) ? String(msgMap[djName] || '') : '';
            pinnedEl.style.display = msg ? 'block' : 'none';
            pinnedEl.textContent = msg || '';
        }};

        // Dışarıdan (program değişince) anlık admin satırını güncellemek için global fonksiyon
        window.setChatAdminName = (djText) => {{
            if (!adminLineEl) return;
            const nm = normalizeName((djText || 'DJ').toString().replace(/^DJ\\s*/i, ''));
            adminLineEl.innerHTML =
                '<span class=\"admin-label\">ADMIN:</span> ' +
                '<span class=\"admin-name\">' + nm + '</span> ' +
                '<span class=\"admin-active\">(aktif)</span>';

            // Chat içinde sabit mesajı da güncelle
            try {{ updatePinnedForDj(djText); }} catch (e) {{}}
        }};

        if (!radioData.ablyEnabled) {{
            const src = radioData.ablyKeySource ? (" (kaynak: " + radioData.ablyKeySource + ")") : "";
            const err = radioData.ablyError ? (" " + radioData.ablyError) : "";
            if (statusEl) statusEl.textContent = "Chat kapalı." + src + err;
            if (sendEl) sendEl.disabled = true;
            return;
        }}

        // Ably script defer ile geliyor; yüklenene kadar kısa süre bekle.
        const waitForAbly = (triesLeft = 80) => {{
            if (typeof Ably !== 'undefined') return true;
            if (triesLeft <= 0) return false;
            return null;
        }};
        const okAbly = waitForAbly();
        if (okAbly === false) {{
            if (statusEl) statusEl.textContent = "Chat yüklenemedi (Ably script).";
            if (sendEl) sendEl.disabled = true;
            return;
        }}
        if (okAbly === null) {{
            if (statusEl) statusEl.textContent = "Chat yükleniyor...";
            if (sendEl) sendEl.disabled = true;
            let tries = 80;
            const t = setInterval(() => {{
                tries -= 1;
                if (typeof Ably !== 'undefined') {{
                    clearInterval(t);
                    try {{ initChat(); }} catch (e) {{}}
                }} else if (tries <= 0) {{
                    clearInterval(t);
                    if (statusEl) statusEl.textContent = "Chat yüklenemedi (Ably script gecikti).";
                }}
            }}, 150);
            return;
        }}

        const realtime = new Ably.Realtime({{
            token: radioData.ablyToken,
        }});
        const channelName = radioData.ablyChannel || 'radyo-chat';
        const channel = realtime.channels.get(channelName);

        const setStatus = (s) => {{ if (statusEl) statusEl.textContent = s; }};
        if (sendEl) sendEl.disabled = true;

        realtime.connection.on((state) => {{
            setStatus("Chat: " + state.current);
        }});

        channel.on((state) => {{
            const reason = (state && state.reason) ? (" (" + (state.reason.message || String(state.reason)) + ")") : "";
            setStatus("Chat: " + realtime.connection.state + " / kanal: " + state.current + reason);
            if (sendEl) sendEl.disabled = !(realtime.connection.state === 'connected' && state.current === 'attached');
        }});

        channel.attach((err) => {{
            if (err) {{
                setStatus("Chat attach hatası: " + (err.message || String(err)));
                if (sendEl) sendEl.disabled = true;
            }}

            // Presence setup
            const memberKeyFromPresence = (p) => {{
                // Ably'de token clientId hepsinde aynı olabilir. Bu yüzden anahtar olarak connectionId/connection.id kullan.
                const conn =
                    p && (p.connectionId || (p.connection && p.connection.id) || p.connection?.id)
                        ? (p.connectionId || (p.connection && p.connection.id) || p.connection?.id)
                        : null;
                if (conn) return String(conn);

                // En azından çakışma olmasın diye clientId'yi en son fallback yap.
                const c = p && p.clientId ? p.clientId : null;
                if (c) return String(c);

                return String((p && p.id) || (p && p.presenceId) || 'unknown');
            }};

            const extractNameFromPresence = (p) => {{
                const nm =
                    p && p.data && p.data.name ? p.data.name :
                    p && p.data ? p.data :
                    p && p.state && p.state.name ? p.state.name :
                    null;
                return normalizeName(nm);
            }};

            const setMyPresenceName = (nm) => {{
                const data = {{ name: normalizeName(nm) }};
                try {{
                    if (channel && channel.presence) {{
                        // Presence'a ilk kez giriş için mutlaka enter kullan (update bazen mevcut presence bekleyebilir)
                        if (typeof channel.presence.enter === 'function') {{
                            channel.presence.enter(data);
                        }} else if (typeof channel.presence.update === 'function') {{
                            channel.presence.update(data);
                        }}
                    }}
                }} catch (_) {{ }}
            }};

            // Sayfa açılınca presence'a gir
            setMyPresenceName((nameEl && nameEl.value ? nameEl.value.trim() : '') || 'Anonim');

            // Mevcut presence'i çek
            const toArrayMembers = (ms) => {{
                if (!ms) return [];
                if (Array.isArray(ms)) return ms;
                if (typeof ms === 'object') {{
                    const vals = Object.values(ms);
                    const out = [];
                    vals.forEach(v => {{
                        if (Array.isArray(v)) out.push(...v);
                        else out.push(v);
                    }});
                    return out;
                }}
                return [];
            }};

            const seedPresence = (members) => {{
                // temizle
                for (const k in activeNameCount) delete activeNameCount[k];
                for (const k in memberIdToName) delete memberIdToName[k];

                const list = toArrayMembers(members);
                list.forEach(p => {{
                    const key = memberKeyFromPresence(p);
                    const nm = extractNameFromPresence(p);
                    memberIdToName[key] = nm;
                    activeNameCount[nm] = (activeNameCount[nm] || 0) + 1;
                }});
                updateActiveColors();
            }};

            try {{
                const g = channel.presence.get();
                if (g && typeof g.then === 'function') {{
                    g.then(m => seedPresence(m)).catch(() => {{ }});
                }} else {{
                    channel.presence.get((_, m) => seedPresence(m));
                }}
            }} catch (_) {{ }}

            try {{
                channel.presence.subscribe('enter', (p) => {{
                    const key = memberKeyFromPresence(p);
                    const nm = extractNameFromPresence(p);
                    memberIdToName[key] = nm;
                    adjustActive(nm, +1);
                    updateActiveColors();
                }});
            }} catch (_) {{ }}

            try {{
                channel.presence.subscribe('leave', (p) => {{
                    const key = memberKeyFromPresence(p);
                    const nm = memberIdToName[key];
                    if (nm) adjustActive(nm, -1);
                    delete memberIdToName[key];
                    updateActiveColors();
                }});
            }} catch (_) {{ }}

            // Sayfadan çıkarken presence bırak (tarayıcı kapanışında opsiyonel)
            try {{
                window.addEventListener('beforeunload', () => {{
                    try {{
                        if (channel && channel.presence && typeof channel.presence.leave === 'function') {{
                            channel.presence.leave();
                        }}
                    }} catch (_) {{ }}
                }});
            }} catch (_) {{ }}
        }});

        channel.subscribe('msg', (m) => {{
            const data = m.data || {{}};
            pushMsg(data.name, data.text);
        }});

        const send = () => {{
            const name = (nameEl && nameEl.value ? nameEl.value.trim() : '') || 'Anonim';
            const text = (textEl && textEl.value ? textEl.value.trim() : '');
            if (!text) return;
            // Tüm filtreler kapalı: herkes serbest mesaj atabilir.

            // Mesaj onaylandı: metin kutusunu temizle
            if (textEl) textEl.value = '';

            // Kullanıcı adını presence'a da yansıt (aktiflik rengi doğru olsun)
            try {{
                if (channel && channel.presence) {{
                    const data = {{ name: normalizeName(name) }};
                    if (typeof channel.presence.update === 'function') {{
                        channel.presence.update(data);
                    }} else if (typeof channel.presence.enter === 'function') {{
                        channel.presence.enter(data);
                    }}
                }}
            }} catch (_) {{ }}

            // Sonra Ably üzerinden yayınla, hata olursa durum satırına yaz
            channel.publish('msg', {{ name, text }}, (err) => {{
                if (err && statusEl) {{
                    statusEl.textContent = "Mesaj gönderilemedi: " + (err.message || String(err));
                }}
            }});
        }};

        if (sendEl) sendEl.onclick = send;
        if (textEl) textEl.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') send(); }});

        pushMsg('Sistem', 'Canlı sohbete hoş geldin.');
        }} catch (e) {{
            // JS hatası audio'nun çalışmasını da engellemesin diye chat içini güvenli kapatıyoruz.
            try {{
                if (statusEl) statusEl.textContent = "Chat hata: " + (e && e.message ? e.message : String(e));
            }} catch (_) {{ }}
        }}
    }})();

    // Sağ üst analog saat (canvas)
    (function initClock() {{
        const canvas = document.getElementById('analogClock');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const draw = () => {{
            const now = new Date();
            const w = canvas.width;
            const h = canvas.height;
            const cx = w / 2;
            const cy = h / 2;
            const r = Math.min(w, h) / 2 - 3;

            ctx.clearRect(0, 0, w, h);

            // Arka daire + cam hissi (siyah-beyaz)
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            const baseGrad = ctx.createRadialGradient(
                cx - r * 0.25, cy - r * 0.25, r * 0.1,
                cx, cy, r
            );
            baseGrad.addColorStop(0, 'rgba(255,255,255,0.10)');
            baseGrad.addColorStop(0.55, 'rgba(255,255,255,0.04)');
            baseGrad.addColorStop(1, 'rgba(255,255,255,0.01)');
            ctx.fillStyle = baseGrad;
            ctx.fill();

            // Dış çerçeve
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.strokeStyle = 'rgba(255,255,255,0.12)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Yansıma (üstten gelen hafif parıltı)
            ctx.save();
            ctx.globalCompositeOperation = 'screen';
            const gloss = ctx.createLinearGradient(cx - r, cy - r, cx + r, cy + r);
            gloss.addColorStop(0, 'rgba(255,255,255,0.18)');
            gloss.addColorStop(0.35, 'rgba(255,255,255,0.05)');
            gloss.addColorStop(1, 'rgba(255,255,255,0.00)');
            ctx.fillStyle = gloss;
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();

            // Saat işaretleri (12 adet)
            ctx.strokeStyle = 'rgba(255,255,255,0.38)';
            ctx.lineWidth = 2;
            for (let i = 0; i < 12; i++) {{
                const ang = (i / 12) * Math.PI * 2 - Math.PI / 2;
                const x1 = cx + Math.cos(ang) * (r - 6);
                const y1 = cy + Math.sin(ang) * (r - 6);
                const x2 = cx + Math.cos(ang) * (r - 2);
                const y2 = cy + Math.sin(ang) * (r - 2);
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.stroke();
            }}

            // Yumuşak kollar: milisaniyeyi de açığa katıyoruz
            const sec = now.getSeconds() + (now.getMilliseconds() / 1000);
            const min = now.getMinutes() + (sec / 60);
            const hr = (now.getHours() % 12) + (min / 60);

            // Kollar
            const hourAng = (hr / 12) * Math.PI * 2 - Math.PI / 2;
            const minAng = (min / 60) * Math.PI * 2 - Math.PI / 2;
            const secAng = (sec / 60) * Math.PI * 2 - Math.PI / 2;

            // Saat kolu
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + Math.cos(hourAng) * (r * 0.62), cy + Math.sin(hourAng) * (r * 0.62));
            ctx.strokeStyle = 'rgba(255,255,255,0.95)';
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.stroke();

            // Dakika kolu
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + Math.cos(minAng) * (r * 0.86), cy + Math.sin(minAng) * (r * 0.86));
            ctx.strokeStyle = 'rgba(255,255,255,0.85)';
            ctx.lineWidth = 1.6;
            ctx.stroke();

            // Saniye kolu
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + Math.cos(secAng) * (r * 0.85), cy + Math.sin(secAng) * (r * 0.85));
            ctx.strokeStyle = 'rgba(255,255,255,0.95)';
            ctx.lineWidth = 1.2;
            ctx.stroke();

            // Merkez nokta
            ctx.beginPath();
            ctx.arc(cx, cy, 2, 0, Math.PI * 2);
            ctx.fillStyle = '#fff';
            ctx.fill();
        }};

        draw();
        // Yumuşak animasyon için requestAnimationFrame (CPU'yu fazla yormamak için 50ms'de bir çiz)
        let lastT = 0;
        const loop = (t) => {{
            if (!lastT || (t - lastT) > 50) {{
                draw();
                lastT = t;
            }}
            requestAnimationFrame(loop);
        }};
        requestAnimationFrame(loop);
    }})();

    // Genel şarkı başlığı biçimlendirici
    function formatTitleFromUrl(url) {{
        const filename = (url.split('/').pop() || '').replace(/\.mp3$/i, '');
        let base = filename;
        try {{
            base = decodeURIComponent(base);
        }} catch (_) {{
            // ignore
        }}

        // Ayırıcıları normalize et
        base = base
            .replace(/\+/g, ' ')
            .replace(/[_]+/g, ' ')
            .replace(/[.]+/g, ' ')
            .replace(/\s*-\s*/g, ' - ')
            .replace(/\s+/g, ' ')
            .trim();

        // YouTube/metadata çöplerini temizle
        const junk = new Set([
            'official', 'video', 'audio', 'clip', 'lyrics', 'lyric', 'hd', 'hq', 'remastered',
            'full', 'version', 'live', 'concert', 'album', 'track', 'music', 'müzik', 'muzik',
            'original', 'ost', 'karaoke'
        ]);

        let partsBase = base.split(' ').filter(Boolean);
        partsBase = partsBase.filter(p => !junk.has(p.toLowerCase()));

        // Sonda rastgele ID gibi duran tokenları at (örn: sbykofwdr2a / 31mcbyjebfc)
        while (partsBase.length > 2) {{
            const last = partsBase[partsBase.length - 1];
            const looksLikeId =
                /^[a-z0-9]{{8,}}$/i.test(last) ||
                (/^[a-z]{{6,}}$/i.test(last) && !/[aeıioöuü]/i.test(last)) ||
                /[0-9]/.test(last);
            if (!looksLikeId) break;
            partsBase.pop();
        }}
        base = partsBase.join(' ');

        const lower = base.toLowerCase();
        let artist = '';
        let namePart = base;

        if (lower.startsWith('grup yorum ')) {{
            artist = 'GRUP YORUM';
            namePart = base.slice('grup yorum '.length);
        }} else if (lower.startsWith('ahmet kaya ')) {{
            artist = 'AHMET KAYA';
            namePart = base.slice('ahmet kaya '.length);
        }} else if (lower.startsWith('yeni turku ')) {{
            artist = 'YENİ TÜRKÜ';
            namePart = base.slice('yeni turku '.length);
        }} else if (lower.startsWith('grup ekin ')) {{
            artist = 'GRUP EKİN';
            namePart = base.slice('grup ekin '.length);
        }} else if (lower.startsWith('grup munzur ')) {{
            artist = 'GRUP MUNZUR';
            namePart = base.slice('grup munzur '.length);
        }}

        const titleCaseTr = (s) => {{
            return s
                .split(' ')
                .filter(Boolean)
                .map(w => {{
                    // küçük bağlaçlar
                    const lw = w.toLowerCase();
                    if (['ve', 'ile', 'ya', 'da', 'de', 'bir', 'i', 'ii', 'iii'].includes(lw)) return lw;
                    return w.charAt(0).toLocaleUpperCase('tr-TR') + w.slice(1).toLocaleLowerCase('tr-TR');
                }})
                .join(' ');
        }};

        const words = namePart.split(' ').filter(Boolean).map(w => {{
            return titleCaseTr(w);
        }});
        let titleCore = words.join(' ');

        // Bazı özel şarkı/ad düzeltmeleri (Türkçe karakterler vb.)
        titleCore = titleCore
            .replace('Cav Bella', 'Çav Bella')
            .replace('Haziranda Olmek Zor', 'Haziranda Ölmek Zor')
            .replace('Hakliyiz Kazanacagiz', 'Haklıyız Kazanacağız');

        if (artist) {{
            return artist + ' - ' + titleCore;
        }}
        return titleCore || base.toLocaleUpperCase('tr-TR');
    }}
    let isMuted = true;
    let newrozIdx = 0;
    const audio = window.audioObj || new Audio();
    window.audioObj = audio;
    let activeKey = null;
    audio.preload = "auto";
    audio.muted = true;
    audio.crossOrigin = "anonymous";
    // Mobilde (özellikle iOS) autoplay davranışını iyileştirmek için
    try {{ audio.playsInline = true; }} catch (_) {{ }}

    function setStatus(text) {{
        const el = document.getElementById('display-song-name');
        if (el) el.innerText = text;
    }}

    // Otomatik skip: ses ilerlemiyorsa bir sonraki parçaya geç
    // (Ama erken atlamayı engellemek için daha sıkı guard'lar var.)
    let playbackOffsetSeconds = 0;
    let lastProgressTime = 0;
    let lastProgressAt = Date.now();
    let lastStuckSkipAt = 0;
    let trackStartAtMs = Date.now();
    let trackStartTime = 0;
    let currentTrackUrlGuard = '';
    let lastAudioErrorAt = 0;
    let trackEndAtMs = 0;
    let programState = {{ key: null, playlist: [], index: 0 }};

    audio.addEventListener('timeupdate', () => {{
        try {{
            const t = audio.currentTime;
            if (typeof t === 'number' && t > lastProgressTime + 0.25) {{
                lastProgressTime = t;
                lastProgressAt = Date.now();
            }}
        }} catch (_) {{}}
    }});

    audio.addEventListener('playing', () => {{
        try {{
            lastProgressTime = audio.currentTime || 0;
            lastProgressAt = Date.now();
        }} catch (_) {{}}
    }});

    audio.addEventListener('error', () => {{
        try {{
            const err = audio.error;
            lastAudioErrorAt = Date.now();
            const msg =
                err && err.message ? err.message :
                (err ? String(err.code || err) : 'Ses yükleme hatası');
            setStatus("SES YÜKLEME HATASI: " + msg);
        }} catch (_) {{}}
    }});

    // Şarkı gerçekten bitince sıradakine geç.
    audio.addEventListener('ended', () => {{
        try {{
            const n = nextTrackInProgram(true);
            if (n && n.url) {{
                setStatus(formatTitleFromUrl(n.url));
            }}
        }} catch (_) {{}}
    }});

    // Her kullanıcıda aynı sırayı üretmek için: gün bazlı deterministik shuffle
    function hashStringToInt(str) {{
        // FNV-1a 32-bit hash
        let h = 2166136261;
        for (let i = 0; i < str.length; i++) {{
            h ^= str.charCodeAt(i);
            h = Math.imul(h, 16777619);
        }}
        return h >>> 0;
    }}

    function mulberry32(a) {{
        return function() {{
            let t = a += 0x6D2B79F5;
            t = Math.imul(t ^ t >>> 15, t | 1);
            t ^= t + Math.imul(t ^ t >>> 7, t | 61);
            return ((t ^ t >>> 14) >>> 0) / 4294967296;
        }};
    }}

    function deterministicShuffle(arr, seedStr) {{
        const a = arr.slice();
        const rng = mulberry32(hashStringToInt(seedStr));
        for (let i = a.length - 1; i > 0; i--) {{
            const j = Math.floor(rng() * (i + 1));
            const tmp = a[i];
            a[i] = a[j];
            a[j] = tmp;
        }}
        return a;
    }}

    function nextTrackInProgram(shouldPlay = true) {{
        try {{
            const pl = (programState && Array.isArray(programState.playlist)) ? programState.playlist : [];
            if (!pl.length) return null;
            programState.index = (programState.index + 1) % pl.length;
            const tr = pl[programState.index];
            if (tr && tr.url) {{
                setSrcAndSeek(tr.url, 0, shouldPlay && !isMuted, tr.duration);
            }}
            return tr || null;
        }} catch (_) {{
            return null;
        }}
    }}

    function safePlay() {{
        try {{
            audio.muted = false;
            audio.volume = 1.0;
            const p = audio.play();
            if (p && typeof p.catch === "function") {{
                p.catch((err) => {{
                    // Bazı tarayıcılarda, kullanıcı etkileşimi olmadan çağrılırsa
                    // NotAllowedError dönebiliyor; bu durumda sadece sessizce çık.
                    if (err && err.name === "NotAllowedError") {{
                        return;
                    }}
                    const msg = (err && err.name) ? (err.name + ": " + (err.message || "")) : String(err);
                    setStatus("SES HATASI: " + msg);
                }});
            }}
        }} catch (err) {{
            const msg = (err && err.name) ? (err.name + ": " + (err.message || "")) : String(err);
            setStatus("SES HATASI: " + msg);
        }}
    }}

    function setSrcAndSeek(url, seekTime, shouldPlay, expectedDurationSec) {{
        audio.src = url;
        // Yeni parçaya geçince "ilerleme yok" sayacını sıfırla.
        currentTrackUrlGuard = url;
        trackStartAtMs = Date.now();
        trackStartTime = seekTime;
        try {{
            const dur = typeof expectedDurationSec === 'number' ? expectedDurationSec : NaN;
            if (typeof dur === 'number' && isFinite(dur) && dur > 0) {{
                const left = Math.max(0, dur - seekTime);
                trackEndAtMs = trackStartAtMs + left * 1000;
            }} else {{
                trackEndAtMs = 0;
            }}
        }} catch (_) {{ trackEndAtMs = 0; }}
        lastProgressAt = Date.now();
        lastProgressTime = seekTime;
        const applySeek = () => {{
            try {{
                let target = seekTime;
                const dur = audio && typeof audio.duration === 'number' ? audio.duration : NaN;
                if (typeof dur === 'number' && isFinite(dur) && dur > 0) {{
                    // duration güvenliyse clamp yap
                    target = Math.min(target, Math.max(0, dur - 0.25));
                }} else {{
                    // duration henüz hazır değilse sona/ilerisine kaçıp bitmiş gibi gösterme.
                    target = 0;
                }}
                audio.currentTime = target;
            }} catch (_) {{ }}
            if (shouldPlay) safePlay();
        }};

        // Bazı tarayıcılarda metadata gelmeden seek hata verir; bu yüzden bekliyoruz.
        if (audio.readyState >= 1) {{
            applySeek();
        }} else {{
            const onMeta = () => {{
                audio.removeEventListener('loadedmetadata', onMeta);
                applySeek();
            }};
            audio.addEventListener('loadedmetadata', onMeta);
        }}
    }}


    function sync() {{
        const h = new Date().getHours();
        let key = "grup_yorum"; 
        let name = "YAYINDA"; 
        let img = radioData.imgs.mozaik;

        if (h >= 0 && h < 3) {{
            key = "ahmet_kaya"; 
            name = "AHMET KAYA"; 
            img = radioData.imgs.ahmet_kaya;
        }} else if (h >= 3 && h < 6) {{
            key = "ermeni_ezgileri"; 
            name = "ERMENİ HALK EZGİLERİ"; 
            img = radioData.imgs.ermeni_ezgileri;
        }} else if (h >= 6 && h < 11) {{
            key = "mozaik"; 
            name = "MOZAİK"; 
            img = radioData.imgs.mozaik;
        }} else if (h >= 11 && h < 14) {{
            key = "tsm"; 
            name = "TSM SAATİ"; 
            img = radioData.imgs.tsm;
        }} else if (h >= 14 && h < 17) {{
            key = "tiyatro"; 
            name = "RADYO TİYATROSU"; 
            img = radioData.imgs.tiyatro;
        }} else if (h >= 17 && h < 20) {{
            key = "soldan_sesler"; 
            name = "SOLDAN SESLER"; 
            img = radioData.imgs.soldan_sesler;
        }} else if (h >= 20 && h < 21) {{
            key = "tasavvuf"; 
            name = "TASAVVUF VAKTİ"; 
            img = radioData.imgs.tasavvuf;
        }} else if (h >= 21 && h < 22) {{
            key = "anadolu_rock"; 
            name = "ANADOLU ROCK"; 
            img = radioData.imgs.anadolu_rock;
        }} else if (h >= 22 && h < 24) {{
            key = "grup_yorum"; 
            name = "GRUP YORUM SAATİ"; 
            img = radioData.imgs.grup_yorum;
        }}
        const basePlaylist = radioData.playlists[key] || [];

        // Her gün 1 kez değişsin ama aynı anda tüm kullanıcılar aynı şarkıyı görsün.
        const dateObj = new Date();
        const dateStr = dateObj.getFullYear() + '-' +
            String(dateObj.getMonth() + 1).padStart(2, '0') + '-' +
            String(dateObj.getDate()).padStart(2, '0');
        const cacheKey = key + '|' + dateStr;

        const dailyShuffledPlaylists = window.dailyShuffledPlaylists || {{}};
        window.dailyShuffledPlaylists = dailyShuffledPlaylists;

        let playlist = dailyShuffledPlaylists[cacheKey];
        if (!playlist || playlist.length !== basePlaylist.length) {{
            playlist = deterministicShuffle(basePlaylist, cacheKey);
            dailyShuffledPlaylists[cacheKey] = playlist;
        }}

        // Süre tablosuna göre seek yapmak yerine, şarkıları sırayla çal.
        // Program saat değişince sadece playlist değişir.
        const programChanged = (!programState.key || programState.key !== key);
        if (programChanged) {{
            programState.key = key;
            programState.playlist = Array.isArray(playlist) ? playlist : [];
            programState.index = 0;
        }} else if (!programState.playlist || programState.playlist.length !== playlist.length) {{
            // Gün değişimi vb. durumlarda günlük shuffle farklılaşabilir.
            programState.playlist = Array.isArray(playlist) ? playlist : [];
            if (programState.index >= programState.playlist.length) programState.index = 0;
        }}

        const currentTrack = (programState.playlist && programState.playlist.length)
            ? programState.playlist[programState.index]
            : null;
        const nextTrack = (programState.playlist && programState.playlist.length)
            ? programState.playlist[(programState.index + 1) % programState.playlist.length]
            : null;
        const seekTime = 0;

        document.getElementById('display-category-name').innerText = name;
        const djText = (radioData.djs && radioData.djs[key]) ? radioData.djs[key] : 'DJ';

        // Sohbet panelinin üstünde admin (anlık DJ) yaz
        if (window.setChatAdminName) {{
            try {{ window.setChatAdminName(djText); }} catch (e) {{}}
        }}

        // Üstteki DJ etiketi (DJ: pembe, isim farklı renk)
        const djTopTextEl = document.getElementById('dj-top-text');
        if (djTopTextEl) {{
            const escapeHtml = (s) => {{
                const t = (s === null || s === undefined) ? '' : String(s);
                return t
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/\"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }};

            const djName = (djText || 'DJ').replace(/^DJ\\s*/i, '') || 'DJ';
            const djImgEl = document.getElementById('dj-top-img');

            const normalizeDjKey = (s) => {{
                const t = (s || '').toString().trim().toLowerCase();
                // Türkçe karakterleri sadeleştir + boşluk/altçizgi/çizgi temizle
                return t
                    .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
                    .replace(/\\s+/g, '')
                    .replace(/[_-]+/g, '_');
            }};
            const djKey = normalizeDjKey(djName);

            const djImages = (radioData && radioData.djImages) ? radioData.djImages : null;
            const pickDjImageUrl = (key) => {{
                if (!djImages) return '';
                try {{
                    for (const k of Object.keys(djImages)) {{
                        if (normalizeDjKey(k) === key) return String(djImages[k] || '');
                    }}
                }} catch (e) {{}}
                return '';
            }};
            const chosenUrl = pickDjImageUrl(djKey);

            const setVisible = (el, v) => {{ if (el) el.style.display = v ? 'block' : 'none'; }};
            // DJ_IMAGE_URLS içinde bu DJ için link varsa onu kullan (tüm DJ'ler için)
            const ok = chosenUrl && !String(chosenUrl).includes('PASTE_');
            if (djImgEl) {{
                if (ok) {{
                    djImgEl.setAttribute('data-base-src', chosenUrl);
                    djImgEl.classList.add('dj-custom');
                }} else {{
                    djImgEl.classList.remove('dj-custom');
                }}
            }}

            // Link varsa göster, yoksa gizle (performans için tek img kullanıyoruz)
            setVisible(djImgEl, ok ? true : false);

            // GIF'ler bazen "gelip gidiyor" çünkü her tick'te cache-bust yapınca yeniden yükleniyor.
            // Bu yüzden sadece DJ/program değiştiğinde veya URL değiştiğinde src set edeceğiz.
            const refreshSrc = (el, force=false) => {{
                if (!el) return;
                const base = (el.getAttribute('data-base-src') || el.getAttribute('src') || '').toString();
                if (!base) return;
                const cleanBase = base.split('?')[0];

                const lastBase = el.getAttribute('data-last-base') || '';
                const should = force || (cleanBase !== lastBase);
                if (!should) return;

                el.setAttribute('data-last-base', cleanBase);
                el.onerror = () => {{
                    // Yüklenemezse alan tamamen boş kalmasın
                    el.style.display = 'none';
                }};

                const bust = `t=${{Date.now()}}`;
                el.src = cleanBase + (cleanBase.includes('?') ? '&' : '?') + bust;
            }};

            const keyChanged = (activeKey !== key);
            if (ok) refreshSrc(djImgEl, keyChanged);
            djTopTextEl.innerHTML =
                '<span class="dj-label">DJ:</span> <span class="dj-name">' + escapeHtml(djName) + '</span>';
        }}

        // (Alttaki DJ alanları CSS ile gizli; yine de değer set edelim)
        const djEl = document.getElementById('display-dj-name');
        if (djEl) djEl.innerText = djText;
        const djNoteEl = document.getElementById('display-dj-note');
        if (djNoteEl) djNoteEl.innerText = 'Canlı yayın ekibi • ' + (djText.replace(/^DJ\\s*/i,'') || 'Bilgi');

        // Görsel: cache'e takılmasın + yüklenemezse fallback
        const diskImgEl = document.getElementById('main-disk-img');
        if (diskImgEl) {{
            diskImgEl.onerror = () => {{
                diskImgEl.onerror = null;
                diskImgEl.src = radioData.imgs.mozaik;
            }};

            // Aynı URL görünse bile bazen cache yüzünden güncellenmiyor → küçük cache-bust
            const bust = `t=${{Math.floor(Date.now() / 10000)}}`;
            const nextSrc = img ? (img + (img.includes('?') ? '&' : '?') + bust) : radioData.imgs.mozaik;
            if (diskImgEl.src !== nextSrc) diskImgEl.src = nextSrc;
        }}
        
        let title = (currentTrack && currentTrack.url)
            ? formatTitleFromUrl(currentTrack.url)
            : "YAYIN YÜKLENİYOR";

        document.getElementById('display-song-name').innerText = title;

        const keyChanged = (activeKey !== key);
        if (keyChanged) activeKey = key;

        // Program değişince üstteki DJ etiketinde pop animasyonu
        if (keyChanged) {{
            const djTopEl = document.getElementById('dj-top');
            if (djTopEl) {{
                djTopEl.classList.remove('dj-top-pop');
                void djTopEl.offsetWidth; // animasyonu tekrar tetiklemek için
                djTopEl.classList.add('dj-top-pop');
            }}
        }}

        // Program değiştiyse (veya ilk açılışta) yeni programın ilk parçasını başlat.
        if (currentTrack && currentTrack.url) {{
            if (programChanged || !audio.src || audio.src !== currentTrack.url) {{
                setSrcAndSeek(currentTrack.url, 0, !isMuted, currentTrack.duration);
            }}
        }}

        // Not: currentTime'ı her tick'te zorlamak bazı tarayıcılarda takılmaya sebep olabiliyor.
        // Bu yüzden sadece parça değişince seek yapıyoruz.

        // Şarkı takıldı / gerçekten ilerleme yoksa otomatik bir sonraki parçaya atla
        try {{
            const now = Date.now();
            const stuckForMs = now - lastProgressAt;
            const tNow = audio && typeof audio.currentTime === 'number' ? audio.currentTime : 0;
            const timeLooksStuck = Math.abs(tNow - lastProgressTime) < 0.35;

            const playingUrl = audio && audio.src ? audio.src : '';
            const urlLooksSameTrack =
                currentTrackUrlGuard && (playingUrl === currentTrackUrlGuard || playingUrl.indexOf(currentTrackUrlGuard) !== -1);

            let hasBuffered = false;
            try {{
                hasBuffered = audio && audio.buffered && audio.buffered.length > 0;
            }} catch (_) {{ hasBuffered = false; }}

            const lowReady = audio && typeof audio.readyState === 'number' ? audio.readyState <= 1 : false;
            const isPaused = !!(audio && audio.paused);
            const shouldSkip =
                (!isMuted) &&
                urlLooksSameTrack &&
                stuckForMs > 11000 &&
                timeLooksStuck &&
                nextTrack && nextTrack.url &&
                (!hasBuffered) &&
                (lowReady || isPaused) &&
                (lastAudioErrorAt && (now - lastAudioErrorAt) < 60000);

            if (shouldSkip && (now - lastStuckSkipAt) > 15000) {{
                lastStuckSkipAt = now;
                const skippedTo = nextTrackInProgram(true);
                if (skippedTo && skippedTo.url) {{
                    setStatus("OTOMATİK ATLA: " + formatTitleFromUrl(skippedTo.url));
                }}
            }}
        }} catch (_) {{}}

        document.querySelectorAll('.row-item').forEach(i => {{
            i.classList.toggle('active', h >= parseInt(i.dataset.start) && h < parseInt(i.dataset.end));
        }});

        // Yayın akışında DJ'yi program adının yanına (parantez içinde) yaz
        try {{
            document.querySelectorAll('[data-title-for]').forEach(el => {{
                const k = el.getAttribute('data-title-for');
                if (!k) return;

                // başlığı bir kez sakla
                const base = el.getAttribute('data-base-title') || el.textContent || '';
                if (!el.getAttribute('data-base-title')) el.setAttribute('data-base-title', base.trim());

                const dj = (radioData.djs && radioData.djs[k]) ? String(radioData.djs[k]) : '';
                const djName = dj.replace(/^DJ\\s*/i, '').trim();

                const bt = el.getAttribute('data-base-title') || base.trim();
                if (djName) {{
                    el.innerHTML = bt + ' <span class=\"dj-inline\">(DJ ' + djName + ')</span>';
                }} else {{
                    el.textContent = bt;
                }}
            }});
        }} catch (e) {{}}

        // Dinleyici sayısını (gerçek Presence yerine) 1-8 arası dönen değer yapıyoruz.
        // Bu, Presence gelmediğinde 0 görünmesini engeller.
        const viewersEl = document.getElementById('viewers');
        const viewers = 1 + (Math.floor(Date.now() / 10000) % 8);
        viewersEl && (viewersEl.innerText = viewers);
    }}

    // Newroz Yazısı Geçişi (5 Saniyede Bir)
    setInterval(() => {{
        newrozIdx = (newrozIdx + 1) % radioData.newroz.length;
        document.getElementById('newroz-sub').innerText = radioData.newroz[newrozIdx];
    }}, 5000);

    document.getElementById('control-button').onclick = () => {{
        isMuted = !isMuted;
        document.getElementById('control-button').innerText = isMuted ? "YAYINI BAŞLAT" : "SESİ KAPAT";
        audio.muted = isMuted;
        audio.volume = 1.0;
        sync();
        if (!isMuted) safePlay();
    }};

    // Mobilde autoplay engelli olabiliyor: ilk dokunuşta sesi açmayı dene.
    // Kullanıcı etkileşimi geldiğinde sadece bir kere çalışır.
    (function autoUnmuteOnce() {{
        const btn = document.getElementById('control-button');
        const tryUnmute = () => {{
            if (!isMuted) return;
            isMuted = false;
            audio.muted = false;
            audio.volume = 1.0;
            if (btn) btn.innerText = "SESİ KAPAT";
            sync();
            safePlay();
        }};
        // Streamlit component/iframe içinde event yakalamak için capture + document kullan
        const opts = {{ once: true, passive: true, capture: true }};
        document.addEventListener('touchstart', tryUnmute, opts);
        document.addEventListener('pointerdown', tryUnmute, opts);
        document.addEventListener('click', tryUnmute, {{ once: true, capture: true }});
        window.addEventListener('touchstart', tryUnmute, {{ once: true, passive: true }});
        window.addEventListener('click', tryUnmute, {{ once: true }});
    }})();

    setInterval(sync, 1000);
    sync();
</script>
</body>
</html>
"""

st.markdown(
    """
<style>
iframe { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; }
#MainMenu, footer, header {visibility: hidden;}
</style>
<script>
// Streamlit iframe'ına autoplay izni ver (bazı tarayıcılarda ses için şart)
(function() {
  const tryFix = () => {
    const frames = document.querySelectorAll('iframe');
    frames.forEach(f => {
      const allow = f.getAttribute('allow') || '';
      if (!allow.includes('autoplay')) {
        f.setAttribute('allow', (allow ? allow + '; ' : '') + 'autoplay');
      }
    });
  };
  tryFix();
  setInterval(tryFix, 1000);
})();
</script>
""",
    unsafe_allow_html=True,
)
components.html(html_code, height=2000)

