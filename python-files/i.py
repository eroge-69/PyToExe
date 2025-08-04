def fit_count(w, h, fw, fh):
    hor1 = fw // w
    ver1 = fh // h
    hor2 = fw // h
    ver2 = fh // w
    return max(hor1 * ver1, hor2 * ver2)

def main():
    form_w = float(input("عرض فرم (cm): "))
    form_h = float(input("طول فرم (cm): "))

    n = int(input("تعداد تراکت‌ها: "))
    tracts = []
    for _ in range(n):
        name = input("نام تراکت: ")
        w = float(input("عرض (cm): "))
        h = float(input("طول (cm): "))
        t = int(input("تیراژ: "))
        tracts.append((name, w, h, t))

    print("\nترکیب‌های ممکن با صرفه اقتصادی:\n")
    for i in range(n):
        name1, w1, h1, t1 = tracts[i]
        fit1 = fit_count(w1, h1, form_w, form_h)
        if fit1 == 0:
            continue
        solo_forms1 = -(-t1 // fit1)  # سقف تقسیم به صورت عدد صحیح
        for j in range(i + 1, n):
            name2, w2, h2, t2 = tracts[j]
            fit2 = fit_count(w2, h2, form_w, form_h)
            if fit2 == 0:
                continue
            solo_forms2 = -(-t2 // fit2)

            # بررسی ترکیب کنار هم (ساده، فرض کنیم فقط جمع عرض یا طول)
            # حالت 1: کنار هم عرضی
            combined_fit_hor = 0
            if (w1 + w2) <= form_w and max(h1, h2) <= form_h:
                combined_fit_hor = (form_w // (w1 + w2)) * (form_h // max(h1, h2))

            # حالت 2: کنار هم عمودی
            combined_fit_ver = 0
            if max(w1, w2) <= form_w and (h1 + h2) <= form_h:
                combined_fit_ver = (form_w // max(w1, w2)) * (form_h // (h1 + h2))

            combined_fit = max(combined_fit_hor, combined_fit_ver)
            if combined_fit == 0:
                continue

            # فرض تقسیم فرم بین دو نوع تراکت
            best_combined_forms = None
            for k in range(1, combined_fit + 1):
                per_form_1 = k
                per_form_2 = combined_fit - k
                if per_form_2 <= 0:
                    continue
                forms_1 = -(-t1 // per_form_1)
                forms_2 = -(-t2 // per_form_2)
                combined_forms = max(forms_1, forms_2)
                if best_combined_forms is None or combined_forms < best_combined_forms:
                    best_combined_forms = combined_forms

            if best_combined_forms is not None and best_combined_forms < (solo_forms1 + solo_forms2):
                print(f"{name1} + {name2} --> فرم ترکیبی: {best_combined_forms} / جدا: {solo_forms1 + solo_forms2}")

if __name__ == "__main__":
    main()
