(defun ZE:SERIAL (Path / fsObj hSn abPth cDrv)
  (vl-load-com)
  (if
    (and
      (setq fsObj(vlax-create-object "Scripting.FileSystemObject"))
      (not
	(vl-catch-all-error-p
	  (setq abPth(vl-catch-all-apply 'vlax-invoke-method
		       (list fsObj 'GetAbsolutePathName Path))
		       ); end setq
		   ); end vl-catch-all-error-p
		); end not
	  ); end and
    (progn
      (setq cDrv(vlax-invoke-method fsObj 'GetDrive
        (vlax-invoke-method fsObj 'GetDriveName abPth
        ); end vlax-invoke-method
      );end vlax-invoke-method
     ); end setq
     (if
       (vl-catch-all-error-p
	  (setq hSn(vl-catch-all-apply 'vlax-get-property
	    (list cDrv 'SerialNumber))))
	    (progn
	      (vlax-release-object cDrv)
	      (setq hSn nil)
	    ); end progn
       ); end if
    (vlax-release-object fsObj)
    ); end progn
   ); end if
  hSn
  ); end of #Asmi_Get_Drive_Serial
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(setq HDLETTER (getenv "SystemDrive"))
(setq MYSERIAL (ZE:SERIAL HDLETTER))
(setq MYSERIAL (/ MYSERIAL 1000))
(setq HDSERIAL (ABS MYSERIAL))
(setq REVHDSER (itoa HDSERIAL))
(setq HDREV (vl-list->string (reverse (vl-string->list REVHDSER))))
(setq HDSERIAL1 (atoi HDREV))
(setq VERSION (substr (ver) 15 2))
(setq VERSION (* (atoi VERSION) 2))
(setq VERSION (itoa VERSION))
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
(defun C:Archcode (/ tmp des dch)
    (cond
        (   (not
                (and
                   (setq tmp (vl-filename-mktemp  "temp_ap.tmp"))
                   (setq des (open tmp "w"))
                   (foreach line
                   '(   
                   "reg1 : dialog {label = \"reg1\" ; value = \"ArchPlan Registration\"; key = \"reg1\" ; width = 45; initial_focus = \"accept\" ; "
                   "     : boxed_column {"
                   "     : row {"
                   "     : edit_box {label = \"Request Code: \"; key = \"arch_req\"; edit_width = 15; edit_limit = 15;}"
				   "     }"				   
				   "     : edit_box {label = \"Serial Key: \"; key = \"ser_code\"; edit_width = 15; edit_limit = 0;}"
                   "     : row {"
				   "     : boxed_column {"
				   "     : text {key = \"text1\"; alignment = centered ; fixed_width_font = true;}"
				   "     }"
				   "     }"
                   "     }"
                   "     : row {children_fixed_width = true;"
                   "     : button {label = \"Generate Code\"; mnemonic = \"P\"; key = \"accept\"; width = 30;}"
                   "     : row {"
                   "	 : button {label = \" Exit \"; mnemonic = \"E\"; key = \"cancel\"; is_cancel = true; width = 12;}"
                   "     }"
                   "     }"
                   "}"
                   )
                (write-line line des)
                    )
                    (not (close des))
                    (< 0 (setq dch (load_dialog tmp)))
                    (new_dialog "reg1" dch)
                )
            )
            (prompt "\nError Loading List Box Dialog.")
        )
        (   t    
   (set_tile "reg1" (strcat "Archplan Keygen"))
   (start_image "flat_img")
   (slide_image 0 0 (dimx_tile "flat_img") (dimy_tile "flat_img") "Archplan.slb (Archlogo)")
   (end_image)
   (check)
   (gen_code)
   (action_tile "accept" "(gen_code)")
   (action_tile "cancel" "(done_dialog)")
   (start_dialog)
   )
  )
(setq dch (unload_dialog dch))       ; Unload the dialog
(if (and tmp (setq tmp (findfile tmp)))
(vl-file-delete tmp))
(princ)
)

(Defun Check (/ v_sion1 v_sion2 v_sion3 v_sion4 inp9 serial_1 serial_2 add_ser1 add_ser2 addzup1 addzup)
(setq v_sion1 (substr (ver) 15 2))
(setq v_sion2 (* (atoi v_sion1) 2))
(setq v_sion3 (itoa v_sion2))
(setq v_sion4 (atoi v_sion1))
(setq inp9 6963946)
(setq serial_1 (getvar "acadver"))
(setq serial_2 (ascii serial_1))
(setq add_ser1 (+ inp9 HDSERIAL1 serial_2))
(setq add_ser2 (* (/ add_ser1 v_sion4) 10))
(setq addzup1 add_ser2)
(setq addzup (strcat (itoa addzup1) v_sion3))
(set_tile "arch_req" addzup)
;(gen_code)
(princ)
)  


(Defun gen_code (/ addser Code_r code_s Code_z Ac_ver addzup2 last6 addzup3 serlen2 inp4 inp3 outp2 Archcode)
(setq addser (get_tile "arch_req"))
(setq Code_r (strlen addser)) ;get the number count
(setq code_s (- code_r 2)) ;remove the last 2 numbers
(setq code_t (- code_r 3)) ; remove 3 from number count and check how many numbers are left
(setq Code_z (substr addser 1 code_t)) ; remove the last 3 numbers fromt from the serial number
(setq Ac_ver (substr addser (+ 1 code_s))) ;get the last 2 numbers from the serial number
(setq Ac_ver (/ (atoi Ac_ver) 2)) ; divide it by 2 to get the Acad version
(setq Ac_ver (itoa Ac_ver)) ; change to string
(setq inp4 (- (atoi Code_z) 1234)) ; subtract numbers
(setq outp2 (+ inp4 853306)) ; add numbers
(setq Archcode (fix outp2)) ; fix the numbers
(setq Archcode (ABS Archcode)) ; Returns the absolute value of a number
(set_tile "ser_code" (itoa Archcode))
(set_tile "text1" (strcat "AutoCad Version: " Ac_ver))
;(if _cancelled 
;    (prompt "\nFunction Cancelled."))
(princ)
)
(princ)