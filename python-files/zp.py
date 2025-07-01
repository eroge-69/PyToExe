zp_clock = 476.8212
rab_time = float(input())
col_smen = rab_time // 8 + 1
zp_base = zp_clock * rab_time
vred = zp_base /10
raion = (zp_base+vred) * 0.25
pit = 165*col_smen
moloko = 746.61/19*col_smen
zp_all = (zp_base+raion+vred+pit+moloko)*0.87
print("Количество смен:", col_smen, 'Зарпалата составит ', round(zp_all,2),'Она состоит из:\n', 'Оклад:', round(zp_base,2), 'Вредность:', round(vred,2), 'Районный коэфициент:', round(raion,2), 'Питание:', round(pit,2), 'Молоко:', round(moloko,2))
