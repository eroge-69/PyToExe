import logging
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import re
import pymysql
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.shared import Pt, Inches
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.validation import add_regex_validation
from ttkbootstrap.widgets import DateEntry
from docx.shared import RGBColor
import zipfile
from io import BytesIO
import os
import winsound
import threading
import tempfile
import time
from docx.enum.text import WD_ALIGN_PARAGRAPH
from ttkbootstrap.constants import *




class ContratApplication:

    def __init__(self, root):
        self.CDD_MASCULIN = """
        طبقًا لأحكام الفصل 6-4 الجديد من مجلة الشغل

        تمهيد:حيث أن شركة أمبار منيف مختصة في صناعة الأحذية للتصدير"Sous Traitance" لفائدة حرفاء بالخارج تفوق في بعض الأحيان حجم قدرتها الإنتاجية العادية، ولما كانت هذه الطلبيات محدودة وغير منتظمة وغير مضمونة الاستمرارية فإن شركة أمبار منيف بحاجة إلى انتداب أجراء لمدة معينة لتلبية حاجياتها الظرفية نظرا للزيادة الغير عادية في حجم العمل المتأتية من ارتفاع طلبيات الحرفاء: Décathlon, Imac , Ricker et Cleon  . يعتبر الطرفان هذا التمهيد جزء من العقد ويلتزمان به كسائر فصوله.
        الحمد لله،
        -  عملا بأحكام مجلة الشغل ومقتضيات الاتفاقية  المشتركة القطاعية لصناعة الأحذية وتوابعها،
        - وبناء على طلب   {{Titre}} {{Prénom}} {{Nom}}  وتصريحه بأنه حر من كل التزام وغير مرتبط بعلاقة شغلية مع أي  مؤجر كان،
        تم الاتفاق والتراضي والتعاقد  بين الممضين أسفله
        أولا : شركة أمبار منيف، شركة خفية الاسم، مقرها الاجتماعي طريق قابس 3060 المحرس، ممثلة في شخص السيد ياسين المنيف بصفته مديرا عاما، المؤجر، من جهة
        ثانيا :  {{Titre}} {{Prénom}} {{Nom}} ، تاريخ الولادة {{DNAIS}}. مكانها {{LNAIS}} عنوان  {{Ville}} صاحب بطاقة التعريف القومية عدد  {{NCIN}} الصادرة بتاريخ {{DCIN}} بـ {{LCIN}}، بصفته متعاقد لمدة معينة، من جهة أخرى
        الفصل الأول : انتدبت شركة أمبار منيف بمقتضى هذا العقد {{Titre}} {{Prénom}} {{Nom}}  ليقع تشغيله بصفة {{Poste}} وذلك بمصنعها الكائن بالعنوان المذكور أو بجميع المصالح التابعة لها.
        الفصل الثاني : مدة العمل وطبيعته : اتفق الطرفان على أن تبدأ العلاقة الشغلية بتاريخ {{DPERIODE}} وتنتهي  بتاريخ  {{FPERIODE}}، وذلك لمدة محدودة قدرها {{DUREE}}.
        الفصل الثالث : يتقاضى {{Titre}} {{Prénom}} {{Nom}} مقابل انجاز العمل موضوع هذا العقد أجرا خاما خاضعا للتنقيصات الاجتماعية والجنائية تفصيله كالآتي :
          أجر أساسي: {{SBASE}} دينار في  {{MPAIE}}
          منح مختلفة: {{PRIME}} دينارًا عن الشهر الكامل
        الفصل الرابع : يعترف الأجير أنه اطلع على تراتيب العمل السارية داخل المؤسسة وتعهد باحترامها بصفتها جزءا لا يتجزأ عن هذا العقد بما في ذلك أوقات العمل، كما يتعهد بالعناية بعملها والمحافظة على ممتلكات المؤسسة من مواد أولية وأدوات وآلات وغيرها، كما أن عليها قبول أي إحالة إلى مركز عمل أو مصلحة يقترحها عليها المؤجر.
        الفصل الخامس : ينتهي هذا العقد بانتهاء أجله المذكور إعلاه بدون سابق إعلام ويصبح الطرفان في حل من العلاقة الشغلية التي تربطهما. كما ينتهي هذا العقد باتفاق الطرفين أو عند انتهاء الأشغال موضوع هذا العقد أو عند قيام الأجير بهفوة فادحة أو ضعف في مؤهلاته أو تدني إنتاجه.
        الفصل السادس : يتعهد  {{Titre}} {{Prénom}} {{Nom}} باحترام سمعة المؤسسة والإمتناع عن إفشاء الأسرار المهنية والصناعية مما ينجر عنه الإضرار بمصالح المؤسسة حتى بعد انتهاء العقد. ويتحمل الأجير مسؤولية كل ضرر ينجر عن مخالفة هذا الشرط ويتعهد بأداء الغرامات اللازمة لجبره بدون مساس بالتتبعات الجزائية طبقا للقانون الجاري به العمل.
        الفصل السابع : يعترف الطرفان أنهما اطلعا على هذا العقد وأمضيا في حالة جواز ومعرفة، ويعينان مقر مخابرتهما بعنوانهما المذكور أعلاه كما يلتزم الأجير بإعلام مؤجره كتابيا بكل تغيير يطرأ عن البيانات الشخصية التي أدل بها بما في ذلك عنوانه ومقر سكناه في ظرف 48 ساعة من تاريخ التغيير.
        حرر بالمحرس في نظيرين بتاريخ {{DATE_CONTRAT}}
          	إمضاء المؤجر وختمه                                                            	 	     إمضاء الأجير معرف ب
        """

        self.CDD_FEMININ = """
        طبقًا لأحكام الفصل 6-4 الجديد من مجلة الشغل 

        تمهيد:حيث أن شركة أمبار منيف مختصة في صناعة الأحذية للتصدير"Sous Traitance" لفائدة حرفاء بالخارج تفوق في بعض الأحيان حجم قدرتها الإنتاجية العادية، ولما كانت هذه الطلبيات محدودة وغير منتظمة وغير مضمونة الاستمرارية فإن شركة أمبار منيف بحاجة إلى انتداب أجراء لمدة معينة لتلبية حاجياتها الظرفية نظرا للزيادة الغير عادية في حجم العمل المتأتية من ارتفاع طلبيات الحرفاء: Décathlon, Imac , Ricker et Cleon  . يعتبر الطرفان هذا التمهيد جزء من العقد ويلتزمان به كسائر فصوله.
        الحمد لله،
        -  عملا بأحكام مجلة الشغل ومقتضيات الاتفاقية  المشتركة القطاعية لصناعة الأحذية وتوابعها،
        - وبناء على طلب   {{Titre}} {{Prénom}} {{Nom}}  وتصريحها بأنها حرة من كل التزام وغير مرتبطة بعلاقة شغلية مع أي  مؤجر كان،
        تم الاتفاق والتراضي والتعاقد  بين الممضين أسفله
        أولا : شركة أمبار منيف، شركة خفية الاسم، مقرها الاجتماعي طريق قابس 3060 المحرس، ممثلة في شخص السيد ياسين المنيف بصفته مديرا عاما، المؤجر، من جهة
        ثانيا :  {{Titre}} {{Prénom}} {{Nom}} ، تاريخ الولادة {{DNAIS}}. مكانها {{LNAIS}} عنوانها {{Ville}} صاحبة بطاقة التعريف القومية عدد  {{NCIN}} الصادرة بتاريخ {{DCIN}} بـ {{LCIN}}، بصفتها {{Poste}} متعاقدة لمدة معينة، من جهة أخرى
        الفصل الأول : انتدبت شركة أمبار منيف بمقتضى هذا العقد {{Titre}} {{Prénom}} {{Nom}}  ليقع تشغيلها بصفة  {{Poste}} وذلك بمصنعها الكائن بالعنوان المذكور أو بجميع المصالح التابعة لها.
        الفصل الثاني : مدة العمل وطبيعته : اتفق الطرفان على أن تبدأ العلاقة الشغلية بتاريخ {{DPERIODE}} وتنتهي  بتاريخ  {{FPERIODE}}، وذلك لمدة محدودة قدرها {{DUREE}}.
        الفصل الثالث : تتقاضى {{Titre}} {{Prénom}} {{Nom}} مقابل انجاز العمل موضوع هذا العقد أجرا خاما خاضعا للتنقيصات الاجتماعية والجنائية تفصيله كالآتي :
          أجر أساسي: {{SBASE}} دينار في {{MPAIE}}
          منح مختلفة: {{PRIME}} دينارًا عن الشهر الكامل
        الفصل الرابع : تعترف الأجيرة أنها اطلعت على تراتيب العمل السارية داخل المؤسسة وتعهدت باحترامها بصفتها جزءا لا يتجزأ عن هذا العقد بما في ذلك أوقات العمل، كما تتعهد بالعناية بعملها والمحافظة على ممتلكات المؤسسة من مواد أولية وأدوات وآلات وغيرها، كما أن عليها قبول أي إحالة إلى مركز عمل أو مصلحة يقترحها عليها المؤجر.
        الفصل الخامس : ينتهي هذا العقد بانتهاء أجله المذكور إعلاه بدون سابق إعلام ويصبح الطرفان في حل من العلاقة الشغلية التي تربطهما. كما ينتهي هذا العقد باتفاق الطرفين أو عند انتهاء الأشغال موضوع هذا العقد أو عند قيام الأجيرة بهفوة فادحة أو ضعف في مؤهلاتها أو تدني إنتاجها.
        الفصل السادس : تتعهد  {{Titre}} {{Prénom}} {{Nom}} باحترام سمعة المؤسسة والإمتناع عن إفشاء الأسرار المهنية والصناعية مما ينجر عنه الإضرار بمصالح المؤسسة حتى بعد انتهاء العقد. وتتحمل الأجيرة مسؤولية كل ضرر ينجر عن مخالفة هذا الشرط وتتعهد بأداء الغرامات اللازمة لجبره بدون مساس بالتتبعات الجزائية طبقا للقانون الجاري به العمل.
        الفصل السابع : يعترف الطرفان أنهما اطلعا على هذا العقد وأمضيا في حالة جواز ومعرفة، ويعينان مقر مخابرتهما بعنوانهما المذكور أعلاه كما تلتزم الأجيرة بإعلام مؤجرها كتابيا بكل تغيير يطرأ عن البيانات الشخصية التي أدلت بها بما في ذلك عنوانها ومقر سكناها في ظرف 48 ساعة من تاريخ التغيير.
        حرر بالمحرس في نظيرين بتاريخ {{DATE_CONTRAT}}
          	إمضاء المؤجر وختمه                                                            	 	     إمضاء الأجيرة معرف ب
        """

        self.CDI_MASCULIN = """
        الحمد لله،
        -  عملا بأحكام مجلة الشغل ومقتضيات الاتفاقية المشتركة القطاعية لصناعة الأحذية وتوابعها،
        وبناء على طلب  {{Titre}} {{Prénom}} {{Nom}} وتصريحه بأنه حر من كل التزام وغير مرتبط بعلاقة شغليه مع أي مؤجر كان،
        تم الاتفاق والتراضي والتعاقد بين الممضين أسفله
        أولا: شركة أمبار منيف، شركة خفية الاسم، مقرها الاجتماعي طريق قابس 3060 المحرس، ممثلة في شخص السيد ياسين المنيف بصفته مديرا عاما، المؤجر، من جهة
        ثانيا : السيد  {{Titre}} {{Prénom}} {{Nom}} تاريخ الولادة {{DNAIS}}. مكانها {{LNAIS}} عنوانه {{Ville}} صاحب بطاقة التعريف القومية عدد {{NCIN}} الصادرة بتاريخ {{DCIN}} بتونس بصفته أجير متعاقد لمدة غير معينة، من جهة أخرى
        الفصل الأول : انتدبت شركة أمبار منيف بمقتضى هذا العقد  {{Titre}} {{Prénom}} {{Nom}} ليقع تشغيله بصفة {{Poste}} وذلك بمصنعها الكائن بالعنوان المذكور أو بجميع المصالح التابعة لها.
        الفصل الثاني : مدة العمل وطبيعته : اتفق الطرفان على أن تبدأ العلاقة الشغلية لمدة غير محددة من تاريخ {{DPERIODE}} .
         يخضع العامل المذكور أعلاه الى فترة تجربة مدتها ستة أشهر قابلة للتجديد مرة واحدة ولنفس المدة ويمكن لاحد طرفي العقد انهاء العمل به قبل انقضاء فترة التجربة بعد اعلام الطرف الأخر باي وسيلة تترك اثرا كتابيا وذلك قبل خمسة عشر يوما من انهاء فترة التجربة.
        الفصل الثالث: يتقاضى  {{Titre}} {{Prénom}} {{Nom}} مقابل انجاز العمل موضوع هذا العقد أجرا خاما خاضعا للتنقيصات الاجتماعية والجنائية تفصيله كالآتي:
        أجر أســـاسي {{SBASE}}   دينار  في الساعة
        منـــح مختلفة {{PRIME}} دينارا  عن الشهر الكامل
        الفصل الرابع: يعترف الأجير أنه اطلع على تراتيب العمل السارية داخل المؤسسة وتعهد باحترامها بصفتها جزءا لا يتجزأ عن هذا العقد بما في ذلك أوقات العمل، كما يتعهد بالعناية بعمله والمحافظة على ممتلكات المؤسسة من مواد أولية وأدوات وآلات وغيرها، كما أن عليه قبول أي إحالة إلى مركز عمل أو مصلحة يقترحها عليه المؤجر. 
        الفصل السادس : يتعهد السيد  {{Titre}} {{Prénom}} {{Nom}} باحترام سمعة المؤسسة والامتناع عن إفشاء الأسرار المهنية والصناعية مما ينجر عنه الإضرار بمصالح المؤسسة حتى بعد انتهاء العقد. ويتحمل الأجير مسؤولية كل ضرر ينجر عن مخالفة هذا الشرط ويتعهد بأداء الغرامات اللازمة لجبره بدون مساس بالتتبعات الجزائية طبقا للقانون الجاري به العمل.
        الفصل السابع: يعترف الطرفان أنهما اطلعا على هذا العقد وأمضيا في حالة جواز ومعرفة، ويعينان مقر مخابرتهما بعنوانهما المذكور أعلاه كما تلتزم الأجيرة بإعلام مؤجرها كتابيا بكل تغيير يطرأ عن البيانات الشخصية التي أدلت بها بما في ذلك عنوانها ومقر سكناها في ظرف 48 ساعة من تاريخ التغيير.
        حرر بالمحرس في نظيرين بتاريخ {{DATE_CONTRAT}}
              إمضاء المؤجر وختمه                     			                    إمضاء الأجير معرف به
        """

        self.CDI_FEMININ = """
        الحمد لله،
        -  عملا بأحكام مجلة الشغل ومقتضيات الاتفاقية المشتركة القطاعية لصناعة الأحذية وتوابعها،
        وبناء على طلب  {{Titre}} {{Prénom}} {{Nom}} وتصريحها بأنها حرة من كل التزام وغير مرتبطة بعلاقة شغليه مع أي مؤجر كان،
        تم الاتفاق والتراضي والتعاقد بين الممضين أسفله
        أولا: شركة أمبار منيف، شركة خفية الاسم، مقرها الاجتماعي طريق قابس 3060 المحرس، ممثلة في شخص السيد ياسين المنيف بصفته مديرا عاما، المؤجر، من جهة
        ثانيا : الآنسة {{Titre}} {{Prénom}} {{Nom}} تاريخ الولادة {{DNAIS}}. مكانها {{LNAIS}} عنوانها {{Ville}} صاحبة بطاقة التعريف القومية عدد {{NCIN}} الصادرة بتاريخ {{DCIN}} بتونس بصفتها أجيرة متعاقدة لمدة غير معينة، من جهة أخرى
        الفصل الأول : انتدبت شركة أمبار منيف بمقتضى هذا العقد  {{Titre}} {{Prénom}} {{Nom}} ليقع تشغيلها بصفة {{Poste}} وذلك بمصنعها الكائن بالعنوان المذكور أو بجميع المصالح التابعة لها.
        الفصل الثاني : مدة العمل وطبيعته : اتفق الطرفان على أن تبدأ العلاقة الشغلية لمدة غير محددة من تاريخ {{DPERIODE}} .
         تخضع العاملة المذكورة أعلاه الى فترة تجربة مدتها ستة أشهر قابلة للتجديد مرة واحدة ولنفس المدة ويمكن لاحد طرفي العقد انهاء العمل به قبل انقضاء فترة التجربة بعد اعلام الطرف الأخر باي وسيلة تترك اثرا كتابيا وذلك قبل خمسة عشر يوما من انهاء فترة التجربة.
        الفصل الثالث: تتقاضى  {{Titre}} {{Prénom}} {{Nom}} مقابل انجاز العمل موضوع هذا العقد أجرا خاما خاضعا للتنقيصات الاجتماعية والجنائية تفصيله كالآتي:
        أجر أســـاسي {{SBASE}}   دينار  في الساعة
        منـــح مختلفة {{PRIME}} دينارا  عن الشهر الكامل
        الفصل الرابع: تعترف الأجيرة أنها اطلعت على تراتيب العمل السارية داخل المؤسسة وتعهدت باحترامها بصفتها جزءا لا يتجزأ عن هذا العقد بما في ذلك أوقات العمل، كما تتعهد بالعناية بعملها والمحافظة على ممتلكات المؤسسة من مواد أولية وأدوات وآلات وغيرها، كما أن عليها قبول أي إحالة إلى مركز عمل أو مصلحة يقترحها عليها المؤجر. 
        الفصل السادس : تتعهد الآنسة {{Titre}} {{Prénom}} {{Nom}} باحترام سمعة المؤسسة والامتناع عن إفشاء الأسرار المهنية والصناعية مما ينجر عنه الإضرار بمصالح المؤسسة حتى بعد انتهاء العقد. وتتحمل الأجيرة مسؤولية كل ضرر ينجر عن مخالفة هذا الشرط وتتعهد بأداء الغرامات اللازمة لجبره بدون مساس بالتتبعات الجزائية طبقا للقانون الجاري به العمل.
        الفصل السابع: يعترف الطرفان أنهما اطلعا على هذا العقد وأمضيا في حالة جواز ومعرفة، ويعينان مقر مخابرتهما بعنوانهما المذكور أعلاه كما تلتزم الأجيرة بإعلام مؤجرها كتابيا بكل تغيير يطرأ عن البيانات الشخصية التي أدلت بها بما في ذلك عنوانها ومقر سكناها في ظرف 48 ساعة من تاريخ التغيير.
        حرر بالمحرس في نظيرين بتاريخ {{DATE_CONTRAT}}
              إمضاء المؤجر وختمه                     			                    إمضاء الأجيرة معرف بها
        """


        self.root = root
        self.root.title("Gestion des Contrats - Imbert Mnif")
        self.root.state('zoomed')
        self.style = ttk.Style(theme='flatly')
        self.style.configure("Treeview", rowheight=30, font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'))
        self.last_contract_check = None
        self.alert_timer = None
        self.check_interval = 1 * 60 * 1000  # 1 minute en millisecondes
        self.alerted_contracts = {}  # Stocker les contrats alertés avec date de fin et timestamp
        self.contract_hash = {}
        self.progress_dialog = None
        self.progress_bar = None
        self.progress_label = None
        self.sound_file = os.path.normpath(r"D:\UIAlert_Notification lasolisa 4 (ID 2066)_LS.wav")
        if not os.path.exists(self.sound_file):
            Messagebox.show_warning(
                f"Le fichier sonore d'alerte n'a pas été trouvé à l'emplacement :\n{self.sound_file}\n\nLes alertes seront silencieuses.",
                "Avertissement",
                parent=root
            )
        self.entries = {}
        self.contract_entries = {}
        self.db_config = {
            "host": "192.168.1.210",
            "user": "omar",
            "password": "1234",
            "database": "rh1",
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        }

        try:
            self.conn = pymysql.connect(**self.db_config)
            self.create_database()
        except pymysql.MySQLError as e:
            Messagebox.show_error(f"Erreur de connexion: {str(e)}", "Erreur")
            self.root.quit()
            return

        self.variables = {
            "genre": tk.StringVar(value="féminin"),
            "matricule": tk.StringVar(),
            "contract_type": tk.StringVar(value="CDD"),
            "salary_type": tk.StringVar(value="hourly")
        }
        self.current_employee = None
        self.logo_path = r"D:\imbertlogo.png"
        self.undo_stack = []
        self.column_definitions = [
            {"text": "Matricule", "stretch": False, "width": 100},
            {"text": "Nom", "stretch": True, "width": 150},
            {"text": "Prénom", "stretch": True, "width": 150},
            {"text": "Genre", "stretch": False, "width": 80},
            {"text": "Date Naissance", "stretch": True, "width": 120},
            {"text": "Lieu Naissance", "stretch": True, "width": 150},
            {"text": "Adresse", "stretch": True, "width": 200},
            {"text": "Ville", "stretch": True, "width": 100},
            {"text": "CIN", "stretch": True, "width": 100},
            {"text": "Date CIN", "stretch": True, "width": 120},
            {"text": "Lieu CIN", "stretch": True, "width": 150},
            {"text": "Poste", "stretch": True, "width": 150},
            {"text": "Email", "stretch": True, "width": 200},
            {"text": "Téléphone", "stretch": True, "width": 120},
            {"text": "Type Contrat", "stretch": True, "width": 100},
            {"text": "Date Début", "stretch": True, "width": 120},
            {"text": "Date Fin", "stretch": True, "width": 120},
            {"text": "Salaire Base", "stretch": True, "width": 100},
            {"text": "Prime", "stretch": True, "width": 100},
            {"text": "Type Salaire", "stretch": True, "width": 100},
        ]
        self.alert_column_definitions = [
            {"text": "Matricule", "stretch": False, "width": 100},
            {"text": "Nom", "stretch": True, "width": 150},
            {"text": "Prénom", "stretch": True, "width": 150},
            {"text": "Date Fin", "stretch": True, "width": 120},
            {"text": "Jours Restants", "stretch": True, "width": 120},
        ]

        self.setup_ui()
        self.load_data()
        self.background_alert_service()





    def show_last_contract(self):
        if not hasattr(self, 'current_employee') or not self.current_employee:
            Messagebox.show_warning("Veuillez d'abord sélectionner un employé", "Attention")
            return

        try:
            with self.conn.cursor() as cursor:
                # Récupérer uniquement le texte du contrat
                cursor.execute('''
                               SELECT texte_contrat
                               FROM contrats
                               WHERE matricule = %s
                               ORDER BY date_creation DESC LIMIT 1
                               ''', (self.current_employee['matricule'],))

                result = cursor.fetchone()

                if result and result[0]:
                    self.display_contract(result[0])
                else:
                    # Générer un nouveau contrat si aucun n'existe
                    contrat_text = self.generate_contract_text(self.current_employee)
                    self.display_contract(contrat_text)

                    # Sauvegarder le nouveau contrat
                    cursor.execute('''
                                   INSERT INTO contrats (matricule, texte_contrat, date_creation)
                                   VALUES (%s, %s, NOW())
                                   ''', (self.current_employee['matricule'], contrat_text))
                    self.conn.commit()

        except Exception as e:
            Messagebox.showerror("Erreur", f"Impossible d'afficher le contrat: {str(e)}")

    def display_contract(self, contract_text):
        """Affiche le contrat dans l'interface"""
        self.contract_text.config(state=tk.NORMAL)
        self.contract_text.delete(1.0, tk.END)
        self.contract_text.insert(tk.END, contract_text, 'rtl')
        self.contract_text.config(state=tk.DISABLED)
        self.notebook.select(2)  # Affiche l'onglet Contrat

    def create_database(self):
        cursor = self.conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS employees (
                matricule VARCHAR(50) PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                genre VARCHAR(20) NOT NULL,
                date_naissance VARCHAR(10),
                lieu_naissance VARCHAR(100),
                adresse VARCHAR(200),
                ville VARCHAR(100) DEFAULT 'المحرس',
                cin VARCHAR(20),
                date_cin VARCHAR(10),
                lieu_cin VARCHAR(100) DEFAULT 'تونس',
                poste VARCHAR(100),
                email VARCHAR(100),
                telephone VARCHAR(20)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS contrats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                matricule VARCHAR(50),
                type_contrat VARCHAR(10),
                date_creation VARCHAR(20),
                texte_contrat TEXT,
                FOREIGN KEY (matricule) REFERENCES employees(matricule)
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matricule ON employees(matricule)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contrat_matricule ON contrats(matricule)")
        self.conn.commit()

    def setup_ui(self):
        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=BOTH, expand=True, padx=15, pady=15)
        self.notebook = ttk.Notebook(main_panel, bootstyle=PRIMARY)
        self.notebook.pack(fill=BOTH, expand=True)

        self.create_employee_tab(main_panel)
        self.create_search_tab(main_panel)
        self.create_contract_tab(main_panel)
        self.create_list_tab(main_panel)
        self.create_alerts_tab(main_panel)

        status_frame = ttk.Frame(main_panel, bootstyle=INFO)
        status_frame.pack(fill=X, pady=(10, 0))

        self.status_var = tk.StringVar(value="Prêt")
        ttk.Label(status_frame, textvariable=self.status_var, bootstyle=(INFO, INVERSE),
                  font=('Segoe UI', 10)).pack(side=LEFT, padx=10)

        ttk.Button(status_frame, text="Aide", command=self.show_help,
                   bootstyle=(INFO, OUTLINE)).pack(side=RIGHT, padx=5)
        ttk.Button(status_frame, text="À propos", command=self.show_about,
                   bootstyle=(INFO, OUTLINE)).pack(side=RIGHT, padx=5)

        self.sound_enabled = True
        ttk.Checkbutton(
            status_frame,
            text="Alertes sonores",
            variable=tk.BooleanVar(value=self.sound_enabled),
            command=lambda: setattr(self, 'sound_enabled', not self.sound_enabled),
            bootstyle="round-toggle"
        ).pack(side=RIGHT, padx=5)

    def create_employee_tab(self, parent):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Nouvel Employé")

        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview, bootstyle=PRIMARY)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        fields = [
            ("Matricule*", "matricule", r'^\w+$', ttk.Entry),
            ("Nom*", "nom", None, ttk.Entry),
            ("Prénom*", "prenom", None, ttk.Entry),
            ("Date Naissance (AAAA-MM-JJ)", "date_naissance", r'^\d{2}/\d{4}/\d{2}$', DateEntry),
            ("Lieu Naissance", "lieu_naissance", None, ttk.Entry),
            ("Adresse", "adresse", None, ttk.Entry),
            ("Ville", "ville", None, ttk.Entry),
            ("Code Postal", "code_postal", r'^\d{4}$', ttk.Entry),
            ("CIN", "cin", r'^\d{8}$', ttk.Entry),
            ("Date CIN (AAAA-MM-JJ)", "date_cin", r'^\d{4}/\d{2}/\d{2}$', DateEntry),
            ("Lieu CIN", "lieu_cin", None, ttk.Entry),
            ("Poste", "poste", None, ttk.Entry),
            ("Email", "email", r'^[^@]+@[^@]+\.[^@]+$', ttk.Entry),
            ("Téléphone", "telephone", r'^\+?\d{10,12}$', ttk.Entry),
            ("Date Embauche (AAAA-MM-JJ)", "date_embauche", r'^\d{4}/\d{2}/\d{2}$', DateEntry),
            ("Dcon", "dcon", None, ttk.Entry),
            ("Durée", "duree", None, ttk.Entry),
            ("Atelier", "atelier", None, ttk.Entry),
            ("Nb Échéances", "nbre_eche", r'^\d+$', ttk.Entry),
            ("Fperiode", "fperiode", None, ttk.Entry),
            ("Degré Polyvalence", "degre_polyvalence", None, ttk.Entry)
        ]

        self.entries = {}
        form_frame = ttk.LabelFrame(scrollable_frame, text="Informations Employé", bootstyle=PRIMARY)
        form_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        for i, (label, field, regex, widget_type) in enumerate(fields):
            ttk.Label(form_frame, text=label, font=('Segoe UI', 10)).grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            entry = widget_type(form_frame, bootstyle="primary") if widget_type != DateEntry else DateEntry(form_frame,
                                                                                                            bootstyle="primary",
                                                                                                            dateformat="%Y-%m-%d")
            if widget_type == DateEntry:
                entry.entry.configure(justify="center")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
            if regex and widget_type == ttk.Entry:
                add_regex_validation(entry, regex)
                entry.bind("<KeyRelease>", lambda e, f=field: self.validate_field(e.widget, f))
            self.entries[field] = entry

        ttk.Label(form_frame, text="Genre*", font=('Segoe UI', 10)).grid(row=len(fields), column=0, sticky=tk.E, padx=5,
                                                                         pady=5)
        genre_frame = ttk.Frame(form_frame)
        genre_frame.grid(row=len(fields), column=1, sticky=tk.W)
        ttk.Radiobutton(genre_frame, text="السيدة", variable=self.variables["genre"], value="السيدة",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(genre_frame, text="الانسة", variable=self.variables["genre"], value="الانسة",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(genre_frame, text="السيد", variable=self.variables["genre"], value="السيد",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)

        self.entries['ville'].insert(0, "المحرس")
        self.entries['lieu_cin'].insert(0, "تونس")

        contract_frame = ttk.LabelFrame(scrollable_frame, text="Détails du Contrat", bootstyle=PRIMARY)
        contract_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        ttk.Label(contract_frame, text="Type de Contrat*", font=('Segoe UI', 10)).grid(row=0, column=0, padx=5, pady=5,
                                                                                       sticky=tk.E)
        ttk.Radiobutton(contract_frame, text="CDD", variable=self.variables["contract_type"], value="CDD",
                        bootstyle="primary-toolbutton", command=self.toggle_date_fin).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(contract_frame, text="CDI", variable=self.variables["contract_type"], value="CDI",
                        bootstyle="primary-toolbutton", command=self.toggle_date_fin).grid(row=0, column=2, sticky=tk.W)

        contract_fields = [
            ("Date Début (AAAA-MM-JJ)*", "date_debut", r'^\d{4}/\d{2}/\d{2}$', DateEntry),
            ("Date Fin (AAAA-MM-JJ)", "date_fin", r'^\d{4}/\d{2}/\d{2}$', DateEntry),
            ("Salaire Base*", "salaire", r'^\d+(\.\d{1,2})?$', ttk.Entry),
            ("Prime*", "prime", r'^\d+(\.\d{1,2})?$', ttk.Entry)
        ]

        self.contract_entries = {}
        for i, (label, field, regex, widget_type) in enumerate(contract_fields):
            ttk.Label(contract_frame, text=label, font=('Segoe UI', 10)).grid(row=i + 1, column=0, padx=5, pady=5,
                                                                              sticky=tk.E)
            entry = widget_type(contract_frame, bootstyle="primary") if widget_type != DateEntry else DateEntry(
                contract_frame, bootstyle="primary", dateformat="%Y-%m-%d")
            if widget_type == DateEntry:
                entry.entry.configure(justify="center")
                if field == "date_fin" and self.variables["contract_type"].get() == "CDI":
                    entry.entry.config(state=tk.DISABLED)
            entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky=tk.EW)
            if regex and widget_type == ttk.Entry:
                add_regex_validation(entry, regex)
                entry.bind("<KeyRelease>", lambda e, f=field: self.validate_field(e.widget, f))
            self.contract_entries[field] = entry

        self.contract_entries['date_debut'].entry.delete(0, tk.END)
        self.contract_entries['date_debut'].entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.contract_entries['salaire'].insert(0, "")
        self.contract_entries['prime'].insert(0, "")

        ttk.Label(contract_frame, text="Type de Salaire*", font=('Segoe UI', 10)).grid(row=len(contract_fields) + 1,
                                                                                       column=0, padx=5, pady=5,
                                                                                       sticky=tk.E)
        salary_type_frame = ttk.Frame(contract_frame)
        salary_type_frame.grid(row=len(contract_fields) + 1, column=1, sticky=tk.W)
        ttk.Radiobutton(salary_type_frame, text="Par Heure", variable=self.variables["salary_type"], value="hourly",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(salary_type_frame, text="Par Mois", variable=self.variables["salary_type"], value="monthly",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Enregistrer et Générer", command=self.save_and_generate, bootstyle=SUCCESS).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Réinitialiser", command=self.clear_form, bootstyle=WARNING).pack(side=tk.LEFT,
                                                                                                        padx=5)

        scrollable_frame.columnconfigure(1, weight=1)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def create_search_tab(self, parent):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Recherche")

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(search_frame, text="Matricule:", font=('Segoe UI', 10)).pack(side=LEFT)

        self.search_combo = ttk.Combobox(search_frame, textvariable=self.variables["matricule"], font=('Segoe UI', 10))
        self.search_combo.pack(side=LEFT, padx=5, expand=True, fill=X)

        ttk.Button(search_frame, text="Rechercher", command=self.search_employee, bootstyle=INFO).pack(side=LEFT,
                                                                                                       padx=5)

        info_frame = ttk.LabelFrame(frame, text="Informations Employé", bootstyle=PRIMARY)
        info_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.info_text = tk.Text(info_frame, wrap=WORD, height=12, font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(info_frame, command=self.info_text.yview, bootstyle=PRIMARY)
        self.info_text.config(yscrollcommand=scrollbar.set)
        self.info_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=X, padx=10, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=X, padx=10, pady=10)

        self.generate_contract_btn = ttk.Button(
            button_frame,
            text="Générer Contrat",
            command=self.generate_and_show_contract,
            bootstyle=SUCCESS,
            state=DISABLED  # Désactivé par défaut
        )
        self.generate_contract_btn.pack(side=LEFT, padx=5)

        self.view_contract_btn = ttk.Button(button_frame, text="Voir Contrat", command=self.show_last_contract,
                                            bootstyle=(PRIMARY, OUTLINE), state=DISABLED)
        self.view_contract_btn.pack(side=LEFT, padx=5)

        self.edit_btn = ttk.Button(button_frame, text="Modifier Employé",
                                   command=lambda: self.edit_employee(self.current_employee['matricule']),
                                   bootstyle=(WARNING, OUTLINE), state=DISABLED)
        self.edit_btn.pack(side=LEFT, padx=5)

        self.delete_btn = ttk.Button(button_frame, text="Supprimer Employé",
                                     command=lambda: self.delete_employee(self.current_employee['matricule']),
                                     bootstyle=(DANGER, OUTLINE), state=DISABLED)
        self.delete_btn.pack(side=LEFT, padx=5)

    def create_contract_tab(self, parent):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Contrat")

        # Configurer le widget Text avec une barre de défilement
        self.contract_text = tk.Text(frame, wrap=tk.WORD, font=('Arial', 11))
        scrollbar = ttk.Scrollbar(frame, command=self.contract_text.yview)
        self.contract_text.configure(yscrollcommand=scrollbar.set)

        # Configurer le texte de droite à gauche (RTL)
        self.contract_text.tag_configure('rtl', justify='right')

        # Disposition
        self.contract_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure text widget for right-to-left appearance
        self.contract_text.tag_configure("rtl", justify="right")
        self.contract_text.insert(tk.END, "", "rtl")  # Apply RTL tag to text

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=X, padx=10, pady=10)
        ttk.Button(button_frame, text="Exporter Word", command=self.export_word, bootstyle=SUCCESS).pack(side=LEFT,
                                                                                                         padx=5)
        ttk.Button(button_frame, text="Copier", command=self.copy_contract, bootstyle=INFO).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Imprimer", command=self.print_contract, bootstyle=PRIMARY).pack(side=LEFT,
                                                                                                       padx=5)

    # Ajoutez la méthode d'impression
    def print_contract(self):
        """Imprime le contrat actuellement affiché et affiche un aperçu"""
        if not self.contract_text.get(1.0, tk.END).strip():
            Messagebox.show_warning("Aucun contrat à imprimer", "Attention")
            return

        try:
            # Create temporary Word document
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"contrat_temp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx")

            # Generate Word document
            doc = self.create_contract_doc(
                self.current_employee['matricule'],
                self.contract_text.get(1.0, tk.END).strip()
            )
            doc.save(temp_file)

            try:
                # Try printing with win32print if available
                import win32print
                import win32api

                printer_name = win32print.GetDefaultPrinter()
                win32api.ShellExecute(
                    0,
                    "print",
                    temp_file,
                    f'/d:"{printer_name}"',
                    temp_dir,
                    0
                )
                self.status_var.set(f"Contrat envoyé à l'imprimante {printer_name}")

            except ImportError:
                # Fallback for systems without win32print
                if os.name == 'posix':
                    subprocess.run(['lpr', temp_file])
                    self.status_var.set("Contrat envoyé à l'imprimante par défaut")
                else:
                    os.startfile(temp_file, "print")
                    self.status_var.set("Ouverture du contrat pour impression")

            # Open the document for preview
            try:
                if os.name == 'nt':
                    os.startfile(temp_file)
                else:
                    subprocess.run(['xdg-open', temp_file])
                Messagebox.show_info(
                    f"Le contrat a été envoyé à l'imprimante et ouvert pour aperçu.\n"
                    f"Fichier temporaire: {temp_file}",
                    "Impression et Aperçu historically"
                )

            except Exception as preview_error:
                Messagebox.show_warning(
                    f"Contrat imprimé, mais erreur lors de l'ouverture de l'aperçu:\n{str(preview_error)}\n"
                    f"Fichier temporaire: {temp_file}",
                    "Avertissement"
                )

        except Exception as e:
            Messagebox.show_error(
                f"Erreur lors de la création/impression du contrat:\n{str(e)}",
                "Erreur d'impression"
            )

    def create_list_tab(self, parent):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Liste Employés")

        # Frame pour les statistiques et actions
        summary_frame = ttk.Frame(frame, bootstyle=INFO)
        summary_frame.pack(fill=X, padx=10, pady=5)

        # Statistiques principales
        stats_frame = ttk.Frame(summary_frame)
        stats_frame.pack(side=LEFT, fill=X, expand=True)

        # Labels pour les statistiques
        self.total_label = ttk.Label(stats_frame, text="Total: 0", font=('Segoe UI', 10))
        self.total_label.pack(side=LEFT, padx=10)

        self.cdd_label = ttk.Label(stats_frame, text="CDD: 0", font=('Segoe UI', 10))
        self.cdd_label.pack(side=LEFT, padx=10)

        self.cdi_label = ttk.Label(stats_frame, text="CDI: 0", font=('Segoe UI', 10))
        self.cdi_label.pack(side=LEFT, padx=10)

        self.salary_label = ttk.Label(stats_frame, text="Salaire Moyen: 0.00 TND", font=('Segoe UI', 10))
        self.salary_label.pack(side=LEFT, padx=10)

        self.prime_label = ttk.Label(stats_frame, text="Prime Moyen: 0.00 TND", font=('Segoe UI', 10))
        self.prime_label.pack(side=LEFT, padx=10)

        # Bouton d'actualisation
        refresh_btn = ttk.Button(
            summary_frame,
            text="🔄 Actualiser",
            command=self.load_employee_table,
            bootstyle=(INFO, OUTLINE)
        )
        refresh_btn.pack(side=RIGHT, padx=5)

        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=X, padx=10, pady=5)
        ttk.Label(filter_frame, text="Filtrer par:", font=('Segoe UI', 10)).pack(side=LEFT)
        self.filter_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                         values=["Nom", "Matricule", "Type Contrat"],
                                         font=('Segoe UI', 10))
        self.filter_combo.pack(side=LEFT, padx=5)
        self.filter_entry = ttk.Entry(filter_frame, font=('Segoe UI', 10))
        self.filter_entry.pack(side=LEFT, padx=5, expand=True, fill=X)
        ttk.Button(filter_frame, text="Filtrer", command=self.apply_filter, bootstyle=INFO).pack(side=LEFT, padx=5)
        ttk.Button(filter_frame, text="Réinitialiser", command=self.reset_filter, bootstyle=WARNING).pack(side=LEFT,
                                                                                                          padx=5)
        ttk.Button(filter_frame, text="Exporter Tous", command=self.export_all_contracts, bootstyle=SUCCESS).pack(
            side=LEFT, padx=5)
        ttk.Button(filter_frame, text="Annuler", command=self.undo_action, bootstyle=(WARNING, OUTLINE)).pack(side=LEFT,
                                                                                                              padx=5)

        self.employee_table = Tableview(
            frame, coldata=self.column_definitions, rowdata=[], paginated=True, searchable=True,
            bootstyle=PRIMARY, autoalign=True, stripecolor=('lightblue', None), pagesize=20
        )
        self.employee_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.employee_table.view.bind("<Double-1>", self.edit_cell)
        self.context_menu = tk.Menu(self.root, tearoff=0, font=('Segoe UI', 10))
        self.context_menu.add_command(label="Modifier", command=self.context_menu_modify)
        self.context_menu.add_command(label="Supprimer", command=self.context_menu_delete)
        self.context_menu.add_command(label="Voir Contrat", command=self.context_menu_view_contract)
        self.context_menu.add_command(label="Exporter Contrat", command=self.context_menu_export_contract)
        self.employee_table.view.bind("<Button-3>", self.show_context_menu)

    def validate_field(self, widget, field):
        value = widget.get()
        validators = {
            "matricule": lambda v: bool(re.match(r'^\w+$', v)) if v else False,
            "cin": lambda v: bool(re.match(r'^\d{8}$', v)) if v else True,
            "date_naissance": lambda v: bool(re.match(r'^\d{4}/\d{2}/\d{2}$', v)) if v else True,
            "date_cin": lambda v: bool(re.match(r'^\d{4}/\d{2}/\d{2}$', v)) if v else True,
            "email": lambda v: bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', v)) if v else True,
            "telephone": lambda v: bool(re.match(r'^\+?\d{10,12}$', v)) if v else True,
            "salaire": lambda v: bool(re.match(r'^\d+(\.\d{1,2})?$', v)) and float(v) > 0 if v else False,
            "prime": lambda v: bool(re.match(r'^\d+(\.\d{1,2})?$', v)) and float(v) >= 0 if v else False,
            "date_debut": lambda v: bool(re.match(r'^\d{4}/\d{2}/\d{2}$', v)) if v else False,
            "date_fin": lambda v: bool(re.match(r'^\d{4}/\d{2}/\d{2}$', v)) if v else True
        }
        widget.configure(bootstyle="danger" if not validators.get(field, lambda x: True)(value) else "primary")

    def toggle_date_fin(self):
        state = DISABLED if self.variables["contract_type"].get() == "CDI" else NORMAL
        self.contract_entries['date_fin'].entry.config(state=state)

    def load_data(self):
        self.load_matricules()
        self.load_employee_table()
        # Vérifier les contrats proches d'expiration après un court délai

    def load_matricules(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT matricule FROM employees ORDER BY matricule")
            self.search_combo['values'] = [row[0] for row in cursor.fetchall()]

    def apply_filter(self):
        filter_type = self.filter_var.get()
        filter_value = self.filter_entry.get().strip().lower()
        if not filter_type or not filter_value:
            self.load_employee_table()
            return

        query = '''
                SELECT e.matricule, \
                       e.nom, \
                       e.prenom, \
                       e.genre, \
                       e.date_naissance, \
                       e.lieu_naissance,
                       e.adresse, \
                       e.ville, \
                       e.cin, \
                       e.date_cin, \
                       e.lieu_cin, \
                       e.poste, \
                       e.email, \
                       e.telephone,
                       c.type_contrat, \
                       c.date_debut, \
                       c.date_fin, \
                       c.salaire_base, \
                       c.prime, \
                       c.salary_type
                FROM employees e
                         LEFT JOIN contrats c ON e.matricule = c.matricule
                    AND c.id = (SELECT MAX(id) FROM contrats WHERE matricule = e.matricule)
                WHERE {} \
                '''
        params = (f"%{filter_value}%",) if filter_type != "Type Contrat" else (filter_value.upper(),)
        condition = {
            "Nom": "LOWER(e.nom) LIKE %s",
            "Matricule": "e.matricule LIKE %s",
            "Type Contrat": "c.type_contrat = %s"
        }.get(filter_type, "1=1")

        with self.conn.cursor() as cursor:
            cursor.execute(query.format(condition), params)
            self.update_table_data(cursor.fetchall())
            self.status_var.set(f"{len(self.employee_table.get_rows())} employés trouvés")

    def reset_filter(self):
        self.filter_var.set("")
        self.filter_entry.delete(0, tk.END)
        self.load_employee_table()

    def show_context_menu(self, event):
        row_id = self.employee_table.view.identify_row(event.y)
        if row_id:
            self.employee_table.view.selection_set(row_id)
            self.selected_matricule = self.employee_table.get_row(row_id).values[0]
            self.context_menu.post(event.x_root, event.y_root)

    def context_menu_modify(self):
        self.edit_employee(self.selected_matricule)

    def context_menu_delete(self):
        self.delete_employee(self.selected_matricule)

    def context_menu_view_contract(self):
        self.current_employee = {'matricule': self.selected_matricule}
        self.show_last_contract()

    def context_menu_export_contract(self):
        self.current_employee = {'matricule': self.selected_matricule}
        self.show_last_contract()
        self.export_word()

    def clear_form(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
            elif isinstance(entry, DateEntry):  # Handle DateEntry differently
                entry.entry.delete(0, tk.END)

        for entry in self.contract_entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
            elif isinstance(entry, DateEntry):  # Handle DateEntry differently
                entry.entry.delete(0, tk.END)
        self.entries['ville'].insert(0, "المحرس")
        self.entries['lieu_cin'].insert(0, "تونس")
        self.contract_entries['date_debut'].entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.contract_entries['salaire'].insert(0, "2500.00")
        self.contract_entries['prime'].insert(0, "500.00")
        self.variables["genre"].set("féminin")
        self.variables["contract_type"].set("CDD")
        self.variables["salary_type"].set("hourly")
        self.status_var.set("Formulaire réinitialisé")

    def view_contract_from_table(self, matricule):
        self.current_employee = {'matricule': matricule}
        self.show_last_contract()

    def export_word(self):
        if not self.current_employee or not isinstance(self.current_employee, dict):
            Messagebox.show_error("Aucun employé sélectionné. Veuillez sélectionner un employé.", "Erreur")
            return

        try:
            doc = self.create_contract_doc(self.current_employee['matricule'])
            if not doc:
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Document Word", "*.docx")],
                initialfile=f"Contrat_{self.current_employee['matricule']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            )
            if not file_path:
                return

            doc.save(file_path)
            Messagebox.show_info(f"Contrat exporté avec succès sous {file_path}.", "Succès")
            self.status_var.set("Contrat exporté avec succès.")

        except Exception as e:
            Messagebox.show_error(f"Erreur lors de l'exportation du contrat: {str(e)}", "Erreur")

################################################################################################

    def create_progress_dialog(self, title, max_value):
        """Create a modal progress dialog with a progress bar."""
        self.progress_dialog = ttk.Toplevel(self.root)
        self.progress_dialog.title(title)
        self.progress_dialog.geometry("400x150")
        self.progress_dialog.transient(self.root)
        self.progress_dialog.grab_set()

        # Label for progress percentage
        self.progress_label = ttk.Label(self.progress_dialog, text="0% (0/0 contrats exportés)")
        self.progress_label.pack(pady=20)

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_dialog,
            maximum=max_value,
            value=0,
            length=350,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)

        # Center dialog
        self.progress_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - self.progress_dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - self.progress_dialog.winfo_height()) // 2
        self.progress_dialog.geometry(f"+{x}+{y}")

    def update_progress(self, current, total):
        """Update the progress bar and label."""
        if self.progress_bar and self.progress_dialog:
            percentage = (current / total) * 100
            self.progress_bar['value'] = current
            self.progress_label.config(text=f"{percentage:.1f}% ({current}/{total} contrats exportés)")
            self.root.update()

    def close_progress_dialog(self):
        """Close the progress dialog."""
        if self.progress_dialog:
            self.progress_dialog.grab_release()
            self.progress_dialog.destroy()
            self.progress_dialog = None
            self.progress_bar = None
            self.progress_label = None

    def export_all_contracts(self):
        try:
            with self.conn.cursor() as cursor:
                # Count total contracts to set progress bar maximum
                cursor.execute("""
                               SELECT COUNT(DISTINCT matricule)
                               FROM contrats
                               """)
                total_contracts = cursor.fetchone()[0]

                if total_contracts == 0:
                    Messagebox.show_info("Aucun contrat à exporter", "Information", parent=self.root)
                    return

                # Create progress dialog
                self.create_progress_dialog("Exportation des contrats", total_contracts)

                # Fetch latest contracts
                cursor.execute("""
                               SELECT c.matricule, c.texte_contrat
                               FROM contrats c
                                        INNER JOIN (SELECT matricule, MAX(date_creation) as max_date
                                                    FROM contrats
                                                    GROUP BY matricule) latest
                                                   ON c.matricule = latest.matricule AND c.date_creation = latest.max_date
                               """)
                contracts = cursor.fetchall()

                folder = filedialog.askdirectory(title="Choisir le dossier de destination")
                if not folder:
                    self.close_progress_dialog()
                    return

                zip_path = os.path.join(folder,
                                        f"contrats_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i, contract in enumerate(contracts, 1):
                        matricule, texte_contrat = contract
                        doc = self.create_contract_doc(matricule, texte_contrat)
                        temp_file = os.path.join(folder, f"contrat_{matricule}.docx")
                        doc.save(temp_file)
                        zipf.write(temp_file, os.path.basename(temp_file))
                        os.remove(temp_file)
                        # Update progress
                        self.update_progress(i, total_contracts)

                self.close_progress_dialog()
                Messagebox.show_info(f"Contrats exportés avec succès dans {zip_path}", "Succès", parent=self.root)
        except Exception as e:
            self.close_progress_dialog()
            Messagebox.show_error(f"Erreur lors de l'exportation: {str(e)}", "Erreur", parent=self.root)

################################################################################################

    def copy_contract(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.contract_text.get(1.0, tk.END))
        self.status_var.set("Texte du contrat copié")

    def edit_cell(self, event):
        row_id = self.employee_table.view.identify_row(event.y)
        column = self.employee_table.view.identify_column(event.x)
        if not row_id or not column:
            return

        col_idx = int(column.replace("#", "")) - 1
        col_name = self.column_definitions[col_idx]["text"]
        if col_name in ["Matricule", "Actions"]:
            return

        row_data = self.employee_table.get_row(row_id).values
        matricule = row_data[0]
        current_value = row_data[col_idx]

        entry = ttk.Entry(self.employee_table.view, bootstyle="primary", font=('Segoe UI', 10))
        entry.insert(0, current_value)
        entry.place(x=event.x_root - self.employee_table.view.winfo_rootx(),
                    y=event.y_root - self.employee_table.view.winfo_rooty(), anchor="nw")

        def validate_input(value):
            validators = {
                "Date Naissance": r'^\d{4}/\d{2}/\d{2}$', "Date CIN": r'^\d{4}/\d{2}/\d{2}$',
                "Date Début": r'^\d{4}/\d{2}/\d{2}$', "Date Fin": r'^\d{4}/\d{2}/\d{2}$',
                "Email": r'^[^@]+@[^@]+\.[^@]+$', "Genre": r'^(féminin|masculin)$',
                "Type Contrat": r'^(CDD|CDI)$', "Salaire Base": r'^\d+(\.\d{1,2})?$',
                "Prime": r'^\d+(\.\d{1,2})?$', "Type Salaire": r'^(hourly|monthly)$'
            }
            return bool(re.match(validators.get(col_name, r'.*'), value)) and (
                float(value) > 0 if col_name in ["Salaire Base", "Prime"] and value else True)

        def save_edit(event=None):
            new_value = entry.get()
            if not validate_input(new_value):
                Messagebox.show_error(f"Valeur invalide pour {col_name}", "Erreur")
                entry.destroy()
                return

            try:
                with self.conn.cursor() as cursor:
                    sql_field = {
                        "Nom": "nom", "Prénom": "prenom", "Genre": "genre", "Date Naissance": "date_naissance",
                        "Lieu Naissance": "lieu_naissance", "Adresse": "adresse", "Ville": "ville",
                        "CIN": "cin", "Date CIN": "date_cin", "Lieu CIN": "lieu_cin", "Poste": "poste",
                        "Email": "email", "Téléphone": "telephone", "Type Contrat": "type_contrat",
                        "Date Début": "date_debut", "Date Fin": "date_fin", "Salaire Base": "salaire_base",
                        "Prime": "prime", "Type Salaire": "salary_type"
                    }.get(col_name)
                    if sql_field:
                        if col_name in ["Type Contrat", "Date Début", "Date Fin", "Salaire Base", "Prime",
                                        "Type Salaire"]:
                            cursor.execute("SELECT id FROM contrats WHERE matricule = %s ORDER BY id DESC LIMIT 1",
                                           (matricule,))
                            contract_id = cursor.fetchone()
                            if contract_id:
                                cursor.execute(f"UPDATE contrats SET {sql_field} = %s WHERE id = %s",
                                               (float(new_value) if col_name in ["Salaire Base",
                                                                                 "Prime"] else new_value,
                                                contract_id[0]))
                                self.undo_stack.append(
                                    ("contract_update", matricule, contract_id[0], sql_field, current_value))
                            else:
                                Messagebox.show_warning("Aucun contrat trouvé", "Attention")
                                entry.destroy()
                                return
                        else:
                            cursor.execute(f"UPDATE employees SET {sql_field} = %s WHERE matricule = %s",
                                           (new_value, matricule))
                            self.undo_stack.append(("employee_update", matricule, sql_field, current_value))
                        self.conn.commit()
                        self.load_employee_table()
                        self.status_var.set(f"Champ {col_name} mis à jour pour {matricule}")
                        if self.current_employee and self.current_employee['matricule'] == matricule:
                            self.search_employee()
            except Exception as e:
                Messagebox.show_error(f"Erreur de mise à jour: {str(e)}", "Erreur")
            finally:
                entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        entry.focus_set()

    def validate_field_value(self, field, value):
        validators = {
            "matricule": lambda v: bool(re.match(r'^\w+$', v)) if v else False,
            "cin": lambda v: bool(re.match(r'^\d{8}$', v)) if v else True,
            "date_naissance": lambda v: self.is_valid_date(v) if v else True,
            "date_cin": lambda v: self.is_valid_date(v) if v else True,
            "email": lambda v: bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', v)) if v else True,
            "telephone": lambda v: bool(re.match(r'^\+?\d{10,12}$', v)) if v else True,
            "salaire": lambda v: bool(re.match(r'^\d+(\.\d{1,2})?$', v)) and float(v) > 0 if v else False,
            "prime": lambda v: bool(re.match(r'^\d+(\.\d{1,2})?$', v)) and float(v) >= 0 if v else False,
            "date_debut": lambda v: self.is_valid_date(v) if v else False,
            "date_fin": lambda v: self.is_valid_date(v) if v else True
        }
        return validators.get(field, lambda x: True)(value)

    def is_valid_date(self, date_str):
        try:
            if not date_str or not re.match(r'^\d{4}/\d{2}/\d{2}$', date_str.strip()):
                return False
            datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def save_employee_and_contract_changes(self, matricule, entries, contract_entries, genre_var, contract_type_var,
                                           salary_type_var, top):
        """Save changes to employee and contract details."""
        try:
            # Helper function to parse and validate date
            def parse_date(entry, field_name):
                date_str = self.get_widget_value(entry)
                if not date_str:
                    return None
                try:
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    return date_obj.strftime("%Y-%m-%d")  # Store in database format
                except ValueError:
                    Messagebox.show_error(f"Format de date invalide pour {field_name} (attendu AAAA-MM-JJ)", "Erreur",
                                          parent=top)
                    raise

            # Collect employee data
            employee_data = {
                "matricule": matricule,  # Use the provided matricule, not from entry
                "nom": self.get_widget_value(entries["nom"]),
                "prenom": self.get_widget_value(entries["prenom"]),
                "genre": genre_var.get(),
                "date_naissance": parse_date(entries["date_naissance"], "Date de Naissance"),
                "lieu_naissance": self.get_widget_value(entries["lieu_naissance"]),
                "ville": self.get_widget_value(entries["ville"]),
                "code_postal": self.get_widget_value(entries["code_postal"]),
                "cin": self.get_widget_value(entries["cin"]),
                "date_cin": parse_date(entries["date_cin"], "Date CIN"),
                "lieu_cin": self.get_widget_value(entries["lieu_cin"]),
                "poste": self.get_widget_value(entries["poste"]),
                "email": self.get_widget_value(entries["email"]),
                "telephone": self.get_widget_value(entries["telephone"]),
                "date_embauche": parse_date(entries["date_embauche"], "Date d'Embauche"),
                "dcon": self.get_widget_value(entries["dcon"]),
                "duree": self.get_widget_value(entries["duree"]),
                "atelier": self.get_widget_value(entries["atelier"]),
                "nbre_eche": self.get_widget_value(entries["nbre_eche"]) or None,
                "fperiode": self.get_widget_value(entries["fperiode"]),
                "degre_polyvalence": self.get_widget_value(entries["degre_polyvalence"]),
                "adresse": self.get_widget_value(entries["adresse"]),
                "salaire_base": self.get_widget_value(contract_entries["salaire"]) or None,
                "prime": self.get_widget_value(contract_entries["prime"]) or None,
                "type_contrat": contract_type_var.get(),
                "salary_type": salary_type_var.get(),
                "date_debut": parse_date(contract_entries["date_debut"], "Date Début"),
                "date_fin": None if contract_type_var.get() == "CDI" else parse_date(contract_entries["date_fin"],
                                                                                     "Date Fin")
            }

            # Validate required fields
            required_fields = ["nom", "prenom", "salaire_base", "date_debut"]
            for field in required_fields:
                if not employee_data[field]:
                    Messagebox.show_error(f"Le champ {field} est requis", "Erreur", parent=top)
                    return

            # Validate numeric fields
            if employee_data["salaire_base"]:
                try:
                    employee_data["salaire_base"] = float(employee_data["salaire_base"])
                    if employee_data["salaire_base"] <= 0:
                        Messagebox.show_error("Le salaire de base doit être supérieur à 0", "Erreur", parent=top)
                        return
                except ValueError:
                    Messagebox.show_error("Le salaire de base doit être un nombre valide", "Erreur", parent=top)
                    return

            if employee_data["prime"]:
                try:
                    employee_data["prime"] = float(employee_data["prime"])
                    if employee_data["prime"] < 0:
                        Messagebox.show_error("La prime ne peut pas être négative", "Erreur", parent=top)
                        return
                except ValueError:
                    Messagebox.show_error("La prime doit être un nombre valide", "Erreur", parent=top)
                    return

            if employee_data["nbre_eche"]:
                try:
                    employee_data["nbre_eche"] = int(employee_data["nbre_eche"])
                    if employee_data["nbre_eche"] < 0:
                        Messagebox.show_error("Le nombre d'échéances ne peut pas être négatif", "Erreur", parent=top)
                        return
                except ValueError:
                    Messagebox.show_error("Le nombre d'échéances doit être un entier", "Erreur", parent=top)
                    return

            # Validate date consistency for CDD
            if employee_data["type_contrat"] == "CDD" and employee_data["date_fin"]:
                debut = datetime.datetime.strptime(employee_data["date_debut"], "%Y-%m-%d")
                fin = datetime.datetime.strptime(employee_data["date_fin"], "%Y-%m-%d")
                if fin <= debut:
                    Messagebox.show_error("La date de fin doit être postérieure à la date de début", "Erreur",
                                          parent=top)
                    return

            # Generate contract text
            contrat_text = self.generate_contract_from_data(employee_data)

            # Update database
            with self.conn.cursor() as cursor:
                # Update employee
                cursor.execute('''
                               UPDATE employees
                               SET nom               = %s,
                                   prenom            = %s,
                                   genre             = %s,
                                   date_naissance    = %s,
                                   lieu_naissance    = %s,
                                   ville             = %s,
                                   code_postal       = %s,
                                   cin               = %s,
                                   date_cin          = %s,
                                   lieu_cin          = %s,
                                   poste             = %s,
                                   email             = %s,
                                   telephone         = %s,
                                   date_embauche     = %s,
                                   dcon              = %s,
                                   duree             = %s,
                                   atelier           = %s,
                                   nbre_eche         = %s,
                                   fperiode          = %s,
                                   degre_polyvalence = %s,
                                   adresse           = %s,
                                   salaire_base      = %s,
                                   prime             = %s,
                                   type_contrat      = %s,
                                   salary_type       = %s,
                                   date_debut        = %s,
                                   date_fin          = %s
                               WHERE matricule = %s
                               ''', (
                                   employee_data["nom"], employee_data["prenom"], employee_data["genre"],
                                   employee_data["date_naissance"], employee_data["lieu_naissance"],
                                   employee_data["ville"],
                                   employee_data["code_postal"], employee_data["cin"], employee_data["date_cin"],
                                   employee_data["lieu_cin"], employee_data["poste"], employee_data["email"],
                                   employee_data["telephone"], employee_data["date_embauche"], employee_data["dcon"],
                                   employee_data["duree"], employee_data["atelier"], employee_data["nbre_eche"],
                                   employee_data["fperiode"], employee_data["degre_polyvalence"],
                                   employee_data["adresse"],
                                   employee_data["salaire_base"], employee_data["prime"], employee_data["type_contrat"],
                                   employee_data["salary_type"], employee_data["date_debut"], employee_data["date_fin"],
                                   matricule
                               ))

                # Update or insert contract
                cursor.execute('''
                               INSERT INTO contrats (matricule, type_contrat, date_creation, texte_contrat)
                               VALUES (%s, %s, CURDATE(), %s) ON DUPLICATE KEY
                               UPDATE
                                   type_contrat =
                               VALUES (type_contrat), date_creation = CURDATE(), texte_contrat =
                               VALUES (texte_contrat)
                               ''', (matricule, employee_data["type_contrat"], contrat_text))

                self.conn.commit()

            # Update UI
            self.load_data()
            self.status_var.set(f"Employé {matricule} mis à jour avec succès")
            Messagebox.show_info("Employé mis à jour avec succès", "Succès", parent=top)
            top.destroy()

        except Exception as e:
            self.conn.rollback()
            Messagebox.show_error(f"Erreur lors de la sauvegarde: {str(e)}", "Erreur", parent=top)

    def delete_employee(self, matricule):
        # Vérification que le matricule est valide (uniquement des chiffres)
        if not matricule or not matricule.isdigit():
            Messagebox.show_error("Matricule invalide", "Erreur")
            return

        # Confirmation de la suppression
        if not Messagebox.yesno(f"Confirmer la suppression de l'employé avec matricule {matricule} ?",
                                "Confirmation de suppression"):
            return

        try:
            with self.conn.cursor() as cursor:
                # Vérifier d'abord si l'employé existe
                cursor.execute("SELECT 1 FROM employees WHERE matricule = %s", (matricule,))
                if not cursor.fetchone():
                    Messagebox.show_error(f"Aucun employé trouvé avec le matricule {matricule}", "Erreur")
                    return

                # Sauvegarde des données pour undo (optionnel)
                cursor.execute("SELECT * FROM employees WHERE matricule = %s", (matricule,))
                employee_data = cursor.fetchone()

                # Suppression des contrats associés
                cursor.execute("DELETE FROM contrats WHERE matricule = %s", (matricule,))

                # Suppression de l'employé
                cursor.execute("DELETE FROM employees WHERE matricule = %s", (matricule,))

                self.conn.commit()

                # Mise à jour de l'interface
                self.load_data()
                self.clear_search()

                # Message de confirmation
                self.status_var.set(f"Employé {matricule} supprimé avec succès")
                Messagebox.show_info(f"L'employé avec matricule {matricule} a été supprimé", "Succès")

        except pymysql.MySQLError as e:
            self.conn.rollback()
            Messagebox.show_error(f"Erreur lors de la suppression : {str(e)}", "Erreur")
            self.status_var.set("Erreur de suppression")

    def undo_action(self):
        if not self.undo_stack:
            Messagebox.show_info("Aucune action à annuler", "Information")
            return

        action_type, matricule, employee_data, contract_data = self.undo_stack.pop()
        try:
            with self.conn.cursor() as cursor:
                if action_type == "employee_delete":
                    cursor.execute('''
                                   INSERT INTO employees (matricule, nom, prenom, genre, date_naissance, lieu_naissance,
                                                          adresse, ville, cin, date_cin, lieu_cin, poste, email,
                                                          telephone)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                   ''', (
                                       employee_data['matricule'], employee_data['nom'], employee_data['prenom'],
                                       employee_data['genre'],
                                       employee_data['date_naissance'], employee_data['lieu_naissance'],
                                       employee_data['adresse'],
                                       employee_data['ville'], employee_data['cin'], employee_data['date_cin'],
                                       employee_data['lieu_cin'],
                                       employee_data['poste'], employee_data['email'], employee_data['telephone']
                                   ))
                    if contract_data:
                        cursor.execute('''
                                       INSERT INTO contrats ( matricule, type_contrat, date_creation, date_debut,
                                                             date_fin, salaire_base, prime, salary_type, texte_contrat)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                       ''', (
                                           contract_data['id'], matricule, contract_data['type_contrat'],
                                           contract_data['date_creation'],
                                           contract_data['date_debut'], contract_data['date_fin'],
                                           contract_data['salaire_base'],
                                           contract_data['prime'], contract_data['salary_type'],
                                           contract_data['texte_contrat']
                                       ))
                    self.status_var.set(f"Suppression de {matricule} annulée")
                elif action_type == "employee_update":
                    cursor.execute(f"UPDATE employees SET {employee_data} = %s WHERE matricule = %s",
                                   (contract_data, matricule))
                    self.status_var.set(f"Mise à jour de {employee_data} pour {matricule} annulée")
                elif action_type == "contract_update":
                    cursor.execute(f"UPDATE contrats SET {employee_data} = %s WHERE id = %s",
                                   (contract_data, matricule))
                    self.status_var.set(f"Mise à jour du contrat pour {matricule} annulée")

                self.conn.commit()
                self.load_data()
                if self.current_employee and self.current_employee['matricule'] == matricule:
                    self.search_employee()
        except pymysql.MySQLError as e:
            Messagebox.show_error(f"Erreur lors de l'annulation: {str(e)}", "Erreur")

    def show_help(self):
        Messagebox.show_info(
            """Application de Gestion des Contrats
    Version: 1.0
    Fonctionnalités:
    - Ajouter, modifier, supprimer des employés
    - Générer des contrats CDD/CDI en arabe
    - Exporter les contrats en Word ou ZIP
    - Rechercher et filtrer les employés
    - Modifier les données directement dans le tableau
    - Annuler la dernière action (suppression ou modification)

    Pour plus d'aide, contactez le support technique.""",
            "Aide"
        )

    def show_about(self):
        Messagebox.show_info(
            """Application de Gestion des Contrats
    Développée par: Omar Badrani
    Version: 1.0
    © Imbert Mnif. Tous droits réservés.""",
            "À propos"
        )
##########################################################################################################


#####################################################################################################
    def on_alert_double_click(self, event):
        """Gérer le double-clic sur une ligne du tableau des alertes pour éditer un employé."""
        try:
            # Identifier la ligne cliquée
            row_id = self.alert_table.view.identify_row(event.y)
            if not row_id or not row_id.startswith('I'):
                Messagebox.show_warning("Aucune ligne valide sélectionnée", "Attention", parent=self.root)
                return

            # Extraire la partie hexadécimale et convertir en index (base 16)
            hex_part = row_id[1:]  # e.g. "00A"
            try:
                index = int(hex_part, 16) - 1  # ✅ CORRECTION ICI
            except ValueError:
                Messagebox.show_error(f"Format d'identifiant invalide: {row_id}", "Erreur", parent=self.root)
                return

            # Vérifier que l'index est dans les limites
            if index < 0 or index >= len(self.alert_table.tablerows):
                Messagebox.show_warning("Ligne sélectionnée hors limites", "Attention", parent=self.root)
                return

            # Obtenir le matricule de la ligne sélectionnée
            selected_row = self.alert_table.tablerows[index]
            matricule = selected_row.values[0]

            # Vérifier la validité du matricule
            if not matricule or not str(matricule).strip().isdigit():
                Messagebox.show_error("Matricule invalide", "Erreur", parent=self.root)
                return

            # Ouvrir la fenêtre d'édition
            self.edit_employee(matricule)

        except Exception as e:
            Messagebox.show_error(f"Erreur inattendue : {str(e)}", "Erreur", parent=self.root)

    def create_alerts_tab(self, parent):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Alertes Contrats")

        alert_frame = ttk.LabelFrame(frame, text="Contrats Expirant dans 30 Jours ou Moins", bootstyle="primary")
        alert_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.alert_table = Tableview(
            alert_frame,
            coldata=self.alert_column_definitions,
            rowdata=[],
            paginated=True,
            searchable=True,
            bootstyle="primary",
            autoalign=True,
            stripecolor=('lightblue', None),
            pagesize=20  # affichage de 20 lignes par page
        )
        self.alert_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Ajouter le binding pour le double-clic
        self.alert_table.view.bind("<Double-1>", self.on_alert_double_click)

        button_frame = ttk.Frame(alert_frame)
        button_frame.pack(fill=X, pady=10)
        ttk.Button(button_frame, text="Actualiser", command=self.load_alert_table, bootstyle="info").pack(side=LEFT,
                                                                                                          padx=5)
        ttk.Button(button_frame, text="Effacer Alertes", command=self.clear_alerts, bootstyle="primary").pack(side=LEFT,
                                                                                                              padx=5)

    def load_alert_table(self):
        """Load the alerts table with expiring contracts."""
        try:
            self.alert_table.delete_rows()
            today = datetime.datetime.now().date().strftime('%Y-%m-%d')

            with self.conn.cursor() as cursor:
                cursor.execute('''
                               SELECT e.matricule,
                                      e.nom,
                                      e.prenom,
                                      e.date_fin,
                                      DATEDIFF(STR_TO_DATE(e.date_fin, '%%Y-%%m-%%d'),
                                               STR_TO_DATE(%s, '%%Y-%%m-%%d')) AS jours_restants
                               FROM employees e
                               WHERE e.type_contrat = 'CDD'
                                 AND e.date_fin IS NOT NULL
                                 AND e.date_fin != ''
                                 AND DATEDIFF(STR_TO_DATE(e.date_fin, '%%Y-%%m-%%d'),
                                              STR_TO_DATE(%s
                                   , '%%Y-%%m-%%d')) BETWEEN 0
                                 AND 30
                               ORDER BY jours_restants
                               ''', (today, today))

                rows = cursor.fetchall()
                for i, row in enumerate(rows):
                    matricule, nom, prenom, date_fin, jours_restants = row
                    date_fin_str = date_fin.strftime('%d/%m/%Y') if date_fin else ''
                    # Include jours_restants in the values for the table
                    self.alert_table.insert_row(
                        values=[matricule, nom, prenom, date_fin_str, str(jours_restants)]
                    )
                    # Log the row ID for debugging
                    row_id = self.alert_table.tablerows[i].iid
                    print(f"Inserted row {i + 1} with ID: {row_id}")

            self.alert_table.load_table_data()
        except Exception as e:
            Messagebox.show_error(f"Erreur lors du chargement des alertes: {str(e)}", "Erreur", parent=self.root)

    def clear_alerts(self):
        self.alerted_contracts.clear()
        self.load_alert_table()
        self.status_var.set("Alertes effacées")

    def check_expiring_contracts(self, force_notification=False):
        """Vérifie les contrats sur le point d'expirer"""
        try:
            today = datetime.datetime.now().date().strftime('%Y-%m-%d')

            with self.conn.cursor() as cursor:
                cursor.execute('''
                               SELECT e.matricule,
                                      e.nom,
                                      e.prenom,
                                      e.date_fin,
                                      DATEDIFF(STR_TO_DATE(e.date_fin, '%%Y-%%m-%%d'),
                                               STR_TO_DATE(%s, '%%Y-%%m-%%d')) AS jours_restants
                               FROM employees e
                               WHERE e.type_contrat = 'CDD'
                                 AND e.date_fin IS NOT NULL
                                 AND e.date_fin != ''
                      AND DATEDIFF(STR_TO_DATE(e.date_fin, '%%Y-%%m-%%d'), 
                           STR_TO_DATE(%s
                                   , '%%Y-%%m-%%d')) BETWEEN 0
                                 AND 30
                               ORDER BY jours_restants
                               ''', (today, today))

                expiring_contracts = cursor.fetchall()

            new_alerts = []
            for contract in expiring_contracts:
                matricule, nom, prenom, date_fin, jours_restants = contract
                contract_key = f"{matricule}_{date_fin}"

                # Vérifie si le contrat a changé ou si l'alerte est forcée
                if contract_key not in self.alerted_contracts or force_notification:
                    new_alerts.append(contract)
                    self.alerted_contracts[contract_key] = {
                        'date_fin': date_fin,
                        'last_alerted': datetime.datetime.now()
                    }
                else:
                    # Vérifie si on doit répéter l'alerte (toutes les 24h)
                    last_alert = self.alerted_contracts[contract_key]['last_alerted']
                    if (datetime.datetime.now() - last_alert).total_seconds() >= 24 * 3600:
                        new_alerts.append(contract)
                        self.alerted_contracts[contract_key]['last_alerted'] = datetime.datetime.now()

            if new_alerts:
                self.show_contract_alerts(new_alerts)
                self.load_alert_table()

        except Exception as e:
            logging.error(f"Erreur lors de la vérification des contrats: {str(e)}")
            self.status_var.set("Erreur vérification alertes")

    def show_contract_alerts(self, contracts):
        """Affiche les alertes de contrat"""
        message = "⚠️ ALERTE : Contrats CDD expirant bientôt ⚠️\n\n"
        for contract in contracts:
            matricule, nom, prenom, date_fin, jours_restants = contract
            message += f"• {nom} {prenom} (Matricule: {matricule}) - "
            message += f"Expire le {date_fin} (dans {jours_restants} jours)\n"

        self.play_alert_sound()
        Messagebox.show_warning(message, "Alerte Contrats", parent=self.root)
        self.stop_alert_sound()
        self.status_var.set(f"⚠ {len(contracts)} nouveaux contrats expirent bientôt")

    def play_alert_sound(self):
        if self.sound_enabled and hasattr(self, 'sound_file') and self.sound_file and os.path.exists(self.sound_file):
            try:
                if os.name == 'nt':
                    def play_loop():
                        while not hasattr(self, 'alert_stopped') or not self.alert_stopped:
                            winsound.PlaySound(self.sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                            time.sleep(2)
                else:
                    def play_loop():
                        while not hasattr(self, 'alert_stopped') or not self.alert_stopped:
                            subprocess.run(['aplay', self.sound_file], check=False)
                            time.sleep(2)

                self.alert_thread = threading.Thread(target=play_loop)
                self.alert_thread.daemon = True
                self.alert_thread.start()
            except Exception as e:
                logging.error(f"Erreur de lecture du son d'alerte: {e}")

    def stop_alert_sound(self):
        """Arrête le son d'alerte"""
        try:
            self.alert_stopped = True
            winsound.PlaySound(None, 0)
            if hasattr(self, 'alert_thread'):
                self.alert_thread.join(timeout=0.1)
        except Exception as e:
            print(f"Erreur lors de l'arrêt du son: {e}")

    def stop_alert_timer(self):
        if self.alert_timer:
            self.root.after_cancel(self.alert_timer)

    def update_summary(self):
        try:
            with self.conn.cursor() as cursor:
                # Compter le nombre total d'employés
                cursor.execute("SELECT COUNT(*) FROM employees")
                total_employees = cursor.fetchone()[0] or 0

                # Compter les CDD et CDI
                cursor.execute("""
                               SELECT SUM(CASE WHEN type_contrat = 'CDD' THEN 1 ELSE 0 END) as cdd_count,
                                      SUM(CASE WHEN type_contrat = 'CDI' THEN 1 ELSE 0 END) as cdi_count,
                                      AVG(salaire_base)as avg_salary,
                                      AVG(prime) as avg_prime
                               FROM employees
                               """)
                stats = cursor.fetchone()

                cdd_count = stats[0] or 0
                cdi_count = stats[1] or 0
                avg_salary = stats[2] or 0
                avg_prime=stats[3] or 0
                # Mettre à jour l'interface
                self.total_label.config(text=f"Total: {total_employees}")
                self.cdd_label.config(text=f"CDD: {cdd_count}")
                self.cdi_label.config(text=f"CDI: {cdi_count}")
                self.salary_label.config(text=f"Salaire Moyen: {avg_salary:.2f} TND")

                self.prime_label.config(text=f"Prime Moyen: {avg_prime:.2f} TND")

        except pymysql.Error as e:
            print(f"Erreur lors de la mise à jour du résumé: {e}")
            self.status_var.set("Erreur statistiques")

    def background_alert_service(self):
        try:
            today = datetime.datetime.now().strftime('%Y-%m-%d')

            with self.conn.cursor() as cursor:
                # Corrected query - using e.date_fin instead of c.date_fin
                cursor.execute('''
                               SELECT e.matricule,
                                      e.nom,
                                      e.prenom,
                                      e.date_fin,
                                      DATEDIFF(STR_TO_DATE(e.date_fin, '%%Y-%%m-%%d'),
                                               STR_TO_DATE(%s, '%%Y-%%m-%%d')) AS jours_restants
                               FROM employees e
                               WHERE e.type_contrat = 'CDD'
                                 AND e.date_fin IS NOT NULL
                                 AND e.date_fin != ''
                      AND DATEDIFF(STR_TO_DATE(e.date_fin, '%%Y-%%m-%%d'),
                                   STR_TO_DATE(%s
                                   , '%%Y-%%m-%%d')) BETWEEN 0
                                 AND 30
                               ORDER BY jours_restants
                               ''', (today, today))

                expiring_contracts = cursor.fetchall()

                if expiring_contracts:
                    message = "⚠️ ALERTE : Contrats CDD expirant bientôt ⚠️\n\n"
                    for contract in expiring_contracts:
                        matricule, nom, prenom, date_fin, jours_restants = contract
                        message += f"• {nom} {prenom} (Matricule: {matricule}) - "
                        message += f"Expire le {date_fin} (dans {jours_restants} jours)\n"

                    if self.sound_enabled and hasattr(self, 'sound_file') and os.path.exists(self.sound_file):
                        try:
                            winsound.PlaySound(self.sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                        except:
                            pass

                    Messagebox.show_warning(message, "Alerte Contrats", parent=self.root)
                    self.status_var.set(f"⚠ {len(expiring_contracts)} contrats expirent bientôt")

        except Exception as e:
            print(f"Erreur dans le service d'alerte: {str(e)}")
        finally:
            self.root.after(self.check_interval, self.background_alert_service)

#####################################################################################################

    def edit_employee(self, matricule):
        """Open a window to edit an employee's details with a scrollable interface."""
        # Create Toplevel window
        top = ttk.Toplevel(self.root)
        top.title(f"Modifier Employé {matricule}")
        top.geometry("900x600")

        # Fetch employee data from database
        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                               SELECT matricule,
                                      nom,
                                      prenom,
                                      genre,
                                      date_naissance,
                                      lieu_naissance,
                                      ville,
                                      cin,
                                      date_cin,
                                      lieu_cin,
                                      poste,
                                      email,
                                      telephone,
                                      type_contrat,
                                      date_debut,
                                      date_fin,
                                      salaire_base,
                                      prime,
                                      salary_type,
                                      adresse,
                                      date_embauche,
                                      code_postal,
                                      dcon,
                                      duree,
                                      atelier,
                                      nbre_eche,
                                      fperiode,
                                      degre_polyvalence
                               FROM employees
                               WHERE matricule = %s
                               ''', (matricule,))
                employee = cursor.fetchone()

                cursor.execute('''
                               SELECT type_contrat, date_creation, texte_contrat
                               FROM contrats
                               WHERE matricule = %s
                               ORDER BY date_creation DESC LIMIT 1
                               ''', (matricule,))
                contract = cursor.fetchone()

            if not employee:
                Messagebox.show_error("Employé non trouvé", "Erreur", parent=top)
                top.destroy()
                return
        except Exception as e:
            Messagebox.show_error(f"Erreur de base de données: {str(e)}", "Erreur", parent=top)
            top.destroy()
            return

        # Create scrollable canvas
        canvas = tk.Canvas(top, highlightthickness=0)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview, bootstyle=PRIMARY)
        scrollable_frame = ttk.Frame(canvas)

        # Configure scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create notebook for employee and contract tabs
        notebook = ttk.Notebook(scrollable_frame, bootstyle=PRIMARY)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        employee_frame = ttk.Frame(notebook)
        contract_frame = ttk.Frame(notebook)
        notebook.add(employee_frame, text="Détails Employé")
        notebook.add(contract_frame, text="Détails Contrat")

        # Initialize variables
        genre_var = tk.StringVar(value=employee[3] or "féminin")
        contract_type_var = tk.StringVar(value=contract[0] if contract else "CDD")
        salary_type_var = tk.StringVar(value=employee[18] or "hourly")
        entries = {}
        contract_entries = {}

        DATE_FORMAT = "%Y-%m-%d"  # Matches database format

        # Helper function to format date for DateEntry
        def format_date_for_entry(date_value):
            if not date_value:
                return ""
            try:
                # Assuming date_value is a string or datetime.date object
                if isinstance(date_value, str):
                    date_obj = datetime.datetime.strptime(date_value, "%Y-%m-%d").date()
                else:
                    date_obj = date_value
                return date_obj.strftime(DATE_FORMAT)
            except (ValueError, TypeError):
                return ""

        # Employee fields
        fields = [
            ("Matricule", "matricule", employee[0], True, ttk.Entry),
            ("Nom", "nom", employee[1], False, ttk.Entry),
            ("Prénom", "prenom", employee[2], False, ttk.Entry),
            ("Date Naissance ", "date_naissance", employee[4], False, ttk.DateEntry),
            ("Lieu Naissance", "lieu_naissance", employee[5], False, ttk.Entry),
            ("Adresse", "adresse", employee[19], False, ttk.Entry),
            ("Ville", "ville", employee[6], False, ttk.Entry),
            ("Code Postal", "code_postal", employee[21], False, ttk.Entry),
            ("CIN", "cin", employee[7], False, ttk.Entry),
            ("Date CIN", "date_cin", employee[8], False, ttk.DateEntry),
            ("Lieu CIN", "lieu_cin", employee[9], False, ttk.Entry),
            ("Poste", "poste", employee[10], False, ttk.Entry),
            ("Email", "email", employee[11], False, ttk.Entry),
            ("Téléphone", "telephone", employee[12], False, ttk.Entry),
            ("Date Embauche ", "date_embauche", employee[20], False, ttk.DateEntry),
            ("Dcon", "dcon", employee[22], False, ttk.Entry),
            ("Durée", "duree", employee[23], False, ttk.Entry),
            ("Atelier", "atelier", employee[24], False, ttk.Entry),
            ("Nb Échéances", "nbre_eche", str(employee[25]) if employee[25] is not None else "", False, ttk.Entry),
            ("Fperiode", "fperiode", employee[26], False, ttk.Entry),
            ("Degré Polyvalence", "degre_polyvalence", employee[27], False, ttk.Entry)
        ]

        # Populate employee fields
        for i, (label, field, value, disabled, widget_type) in enumerate(fields):
            ttk.Label(employee_frame, text=label, font=('Segoe UI', 10)).grid(row=i, column=0, padx=5, pady=5,
                                                                              sticky=tk.E)
            if widget_type == ttk.DateEntry:
                entry = widget_type(employee_frame, bootstyle="primary", dateformat=DATE_FORMAT)
                formatted_date = format_date_for_entry(value)
                if formatted_date:
                    entry.entry.delete(0, tk.END)
                    entry.entry.insert(0, formatted_date)
            else:
                entry = widget_type(employee_frame, bootstyle="primary")
                entry.insert(0, value or "")
            if disabled:
                entry.config(state='disabled')
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
            entries[field] = entry

        # Gender selection
        ttk.Label(employee_frame, text="Genre*", font=('Segoe UI', 10)).grid(
            row=len(fields), column=0, sticky=tk.E, padx=5, pady=5)
        genre_frame = ttk.Frame(employee_frame)
        genre_frame.grid(row=len(fields), column=1, sticky=tk.W)
        ttk.Radiobutton(genre_frame, text="Féminin", variable=genre_var, value="féminin",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(genre_frame, text="Masculin", variable=genre_var, value="masculin",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)

        # Contract fields
        contract_fields = [
            ("Type de Contrat", "type_contrat", contract[0] if contract else "CDD", False, None),
            ("Date Début", "date_debut", employee[14], False, ttk.DateEntry),
            ("Date Fin ", "date_fin", employee[15], contract_type_var.get() == "CDI", ttk.DateEntry),
            ("Salaire Base*", "salaire", str(employee[16]) if employee[16] is not None else "", False, ttk.Entry),
            ("Prime*", "prime", str(employee[17]) if employee[17] is not None else "", False, ttk.Entry)
        ]

        # Populate contract fields
        for i, (label, field, value, disabled, widget_type) in enumerate(contract_fields):
            ttk.Label(contract_frame, text=label, font=('Segoe UI', 10)).grid(row=i, column=0, padx=5, pady=5,
                                                                              sticky=tk.E)
            if field == "type_contrat":
                frame = ttk.Frame(contract_frame)
                frame.grid(row=i, column=1, sticky=tk.W)
                ttk.Radiobutton(frame, text="CDD", variable=contract_type_var, value="CDD",
                                bootstyle="primary-toolbutton",
                                command=lambda: contract_entries['date_fin'].entry.config(state=tk.NORMAL)).pack(
                    side=tk.LEFT, padx=5)
                ttk.Radiobutton(frame, text="CDI", variable=contract_type_var, value="CDI",
                                bootstyle="primary-toolbutton",
                                command=lambda: contract_entries['date_fin'].entry.config(state=tk.DISABLED)).pack(
                    side=tk.LEFT, padx=5)
            else:
                if widget_type == ttk.DateEntry:
                    entry = widget_type(contract_frame, bootstyle="primary", dateformat=DATE_FORMAT)
                    formatted_date = format_date_for_entry(value)
                    if formatted_date:
                        entry.entry.delete(0, tk.END)
                        entry.entry.insert(0, formatted_date)
                    if disabled:
                        entry.entry.config(state='disabled')
                else:
                    entry = widget_type(contract_frame, bootstyle="primary")
                    entry.insert(0, value or "")
                entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
                contract_entries[field] = entry

        # Salary type selection
        ttk.Label(contract_frame, text="Type de Salaire*", font=('Segoe UI', 10)).grid(
            row=len(contract_fields), column=0, padx=5, pady=5, sticky=tk.E)
        salary_type_frame = ttk.Frame(contract_frame)
        salary_type_frame.grid(row=len(contract_fields), column=1, sticky=tk.W)
        ttk.Radiobutton(salary_type_frame, text="Par Heure", variable=salary_type_var, value="hourly",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(salary_type_frame, text="Par Mois", variable=salary_type_var, value="monthly",
                        bootstyle="primary-toolbutton").pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Enregistrer",
                   command=lambda: self.save_employee_and_contract_changes(
                       matricule, entries, contract_entries, genre_var, contract_type_var, salary_type_var, top),
                   bootstyle=SUCCESS).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=top.destroy, bootstyle=WARNING).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        employee_frame.columnconfigure(1, weight=1)
        contract_frame.columnconfigure(1, weight=1)

        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            try:
                delta = 0
                if event.num == 4:  # Linux scroll up
                    delta = -1
                elif event.num == 5:  # Linux scroll down
                    delta = 1
                elif event.delta:  # Windows and macOS
                    delta = -1 * (event.delta // 120)
                if delta:
                    canvas.yview_scroll(int(delta), "units")
            except tk.TclError:
                pass

        # Bind mouse wheel to Toplevel window (cross-platform)
        top.bind("<MouseWheel>", on_mousewheel)  # Windows
        top.bind("<Button-4>", on_mousewheel)  # Linux scroll up
        top.bind("<Button-5>", on_mousewheel)  # Linux scroll down

        # Unbind mouse wheel when Toplevel is destroyed
        def on_destroy():
            top.unbind("<MouseWheel>")
            top.unbind("<Button-4>")
            top.unbind("<Button-5>")
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", on_destroy)

    def __del__(self):
        self.stop_alert_timer()
        self.stop_alert_sound()
        if hasattr(self, 'conn'):
            try:
                self.conn.close()
            except:
                pass

    def get_widget_value(self, widget):
        """Obtient la valeur de n'importe quel widget"""
        if isinstance(widget, (ttk.Entry, ttk.Combobox)):
            return widget.get().strip()
        elif isinstance(widget, DateEntry):
            return widget.entry.get().strip()
        elif hasattr(widget, 'get'):
            return widget.get().strip()
        return ""

    def create_contract_doc(self, matricule, texte=None):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                           SELECT e.matricule,
                                  e.nom,
                                  e.prenom,
                                  e.genre,
                                  e.date_naissance,
                                  e.lieu_naissance,
                                  e.ville,
                                  e.cin,
                                  e.date_cin,
                                  e.lieu_cin,
                                  e.poste,
                                  e.type_contrat,
                                  e.date_debut,
                                  e.date_fin,
                                  e.salaire_base,
                                  e.prime,
                                  e.salary_type,
                                  e.adresse,
                                  e.date_embauche,
                                  e.code_postal,
                                  e.dcon,
                                  e.duree,
                                  e.atelier,
                                  e.nbre_eche,
                                  e.fperiode,
                                  e.degre_polyvalence,
                                  c.texte_contrat
                           FROM employees e
                                    LEFT JOIN contrats c ON e.matricule = c.matricule
                           WHERE e.matricule = %s
                           ORDER BY c.date_creation DESC LIMIT 1
                           ''', (matricule,))
            result = cursor.fetchone()

            if not result:
                Messagebox.show_error("Employé non trouvé", "Erreur")
                return None

            employee_data = {
                'matricule': result[0] or "غير محدد",
                'nom': result[1] or "غير محدد",
                'prenom': result[2] or "غير محدد",
                'genre': result[3] or "غير محدد",
                'date_naissance': result[4] or None,
                'lieu_naissance': result[5] or "غير محدد",
                'ville': result[6] or "غير محدد",
                'cin': result[7] or "غير محدد",
                'date_cin': result[8] or None,
                'lieu_cin': result[9] or "غير محدد",
                'poste': result[10] or "غير محدد",
                'type_contrat': result[11] or "غير محدد",
                'date_debut': result[12] or None,
                'date_fin': result[13] or None,
                'salaire_base': float(result[14] or 0),
                'prime': float(result[15] or 0),
                'salary_type': "الساعة" if result[16] == "hourly" else "الشهر",
                'adresse': result[17] or "غير محدد",
                'date_embauche': result[18] or None,
                'code_postal': result[19] or "غير محدد",
                'dcon': result[20] or "غير محدد",
                'duree': result[21] or "غير محدد",
                'atelier': result[22] or "غير محدد",
                'nbre_eche': result[23] or 0,
                'fperiode': result[24] or "غير محدد",
                'degre_polyvalence': result[25] or "غير محدد"
            }
            texte_contrat = result[26] if result[26] else texte

        if not texte_contrat:
            texte_contrat = self.generate_contract_from_data(employee_data)

        doc = Document()
        section = doc.sections[0]
        section.left_margin = section.right_margin = Inches(8 / 25.4)
        section.top_margin = section.bottom_margin = Inches(5 / 25.4)
        section.is_right_to_left = True

        # ======================================================================
        # EN-TÊTE UNIFIÉ AVEC BORDURE EXTÉRIEURE
        # ======================================================================
        header_table = doc.add_table(rows=1, cols=3)
        header_table.style = 'Table Grid'
        header_table.columns[0].width = Inches(1.5)
        header_table.columns[1].width = Inches(8)
        header_table.columns[2].width = Inches(4)
        header_table.rows[0].height = Inches(1.5)

        # Cellule logo (gauche)
        logo_cell = header_table.cell(0, 0)
        try:
            logo_para = logo_cell.add_paragraph()
            logo_run = logo_para.add_run()
            logo_run.add_picture(self.logo_path, width=Inches(0.4), height=Inches(0.4))
            logo_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception as e:
            print(f"Erreur lors du chargement du logo : {e}")
            logo_cell.text = ""

        # Cellule centrale avec le titre
        title_cell = header_table.cell(0, 1)
        title_para = title_cell.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Titre français
        french_title = title_para.add_run("FORMULAIRE\n")
        french_title.bold = True
        french_title.font.name = "Helvetica"
        french_title.font.size = Pt(8)
        french_title.font.rtl = True

        # Titre arabe
        arabic_title = title_para.add_run(
            f"عقد شغل لمدة {'غير محددة' if employee_data['type_contrat'] == 'CDI' else 'محددة'}\n")
        arabic_title.bold = True
        arabic_title.font.name = "Arial"
        arabic_title.font.size = Pt(8)
        arabic_title.font.rtl = True

        # Cellule droite (informations)
        info_cell = header_table.cell(0, 2)
        info_table = info_cell.add_table(rows=4, cols=2)
        info_table.style = 'Table Grid'
        info_table.columns[0].width = Inches(1.5)
        info_table.columns[1].width = Inches(1.5)

        # Données (Réf, Date, Version, Page)
        is_cdi = employee_data['type_contrat'] == 'CDI'
        info_data = [
            ("Réf.", "FO-RH-04" if is_cdi else "FO-RH-03"),
            ("Date", datetime.datetime.now().strftime('%d/%m/%Y')),
            ("Version", "01"),
            ("Page", "1/1")
        ]

        for row_idx, (label, value) in enumerate(info_data):
            label_cell = info_table.cell(row_idx, 0)
            label_para = label_cell.add_paragraph(label)
            label_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            label_run = label_para.runs[0]
            label_run.font.name = "Helvetica"
            label_run.font.size = Pt(7)
            label_run.font.color.rgb = RGBColor(100, 100, 100)

            value_cell = info_table.cell(row_idx, 1)
            value_para = value_cell.add_paragraph(value)
            value_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            value_run = value_para.runs[0]
            value_run.font.name = "Helvetica"
            value_run.font.size = Pt(7)

        # ======================================================================
        # CORPS DU DOCUMENT
        # ======================================================================
        doc.add_paragraph().paragraph_format.space_after = Pt(12)

        # Matricule de l'employé
        matricule_para = doc.add_paragraph()
        matricule_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        matricule_run = matricule_para.add_run(f"Matricule: {employee_data['matricule']}")
        matricule_run.bold = True
        matricule_run.font.name = "Arial"
        matricule_run.font.size = Pt(9)

        # Espace avant le texte du contrat
        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # Ajout du texte du contrat
        for paragraph in texte_contrat.strip().split('\n'):
            if paragraph.strip():
                body_para = doc.add_paragraph()
                body_para.paragraph_format.space_after = Pt(4)
                body_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                body_run = body_para.add_run(paragraph.strip())
                body_run.font.name = "Arial"
                body_run.font.size = Pt(9)
                body_run.font.rtl = True

        return doc

    def select_contract_template(self, genre, type_contrat):
        # Normalize inputs
        genre = (genre or "").strip()
        type_contrat = (type_contrat or "").strip().upper()

        # Log for debugging
        print(f"Selecting template with genre: '{genre}', type_contrat: '{type_contrat}'")

        if type_contrat == "CDD":
            if genre in ["السيدة","الانسة","الأنسة"]:
                return self.CDD_FEMININ
            elif genre == "السيد":
                return self.CDD_MASCULIN
        elif type_contrat == "CDI":
            if genre in ["السيدة", "الأنسة"]:
                return self.CDI_FEMININ
            elif genre == "السيد":
                return self.CDI_MASCULIN

        # Log warning for invalid inputs
        print(f"Warning: No template found for genre='{genre}', type_contrat='{type_contrat}'")
        Messagebox.show_warning(
            f"Données invalides: genre='{genre}', type_contrat='{type_contrat}'. Veuillez vérifier les données de l'employé.",
            "Avertissement"
        )
        return None

    def generate_contract_from_data(self, employee_data):
        def safe_date_format(date_str, default="غير محدد"):
            if not date_str:
                print(f"Date is None or empty: {date_str}")
                return default
            try:
                if isinstance(date_str, str):
                    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]:
                        try:
                            date_obj = datetime.datetime.strptime(date_str, fmt)
                            return date_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                    print(f"Failed to parse date: {date_str}")
                    return default
                elif isinstance(date_str, datetime.date):
                    return date_str.strftime("%Y-%m-%d")
                print(f"Unexpected date type: {type(date_str)}")
                return default
            except Exception as e:
                print(f"Error parsing date {date_str}: {str(e)}")
                return default

        data = {
            'Titre': employee_data['genre'] or "غير محدد",
            'Prénom': employee_data['prenom'] or "غير محدد",
            'Nom': employee_data['nom'] or "غير محدد",
            'DNAIS': safe_date_format(employee_data.get('date_naissance')),
            'LNAIS': employee_data.get('lieu_naissance', 'غير محدد'),
            'Ville': employee_data.get('adresse', 'غير محدد'),
            'NCIN': employee_data.get('cin', 'غير محدد'),
            'DCIN': safe_date_format(employee_data.get('date_cin')),
            'LCIN': employee_data.get('lieu_cin', 'غير محدد'),
            'Poste': employee_data.get('poste', 'غير محدد'),
            'DPERIODE': safe_date_format(employee_data.get('date_debut')),
            'FPERIODE': safe_date_format(employee_data.get('date_fin')),
            'SBASE': str(employee_data.get('salaire_base', 0)),
            'PRIME': str(employee_data.get('prime', 0)),
            'MPAIE': "الساعة" if employee_data.get('salary_type') == "hourly" else "الشهر",
            'DATE_CONTRAT': datetime.datetime.now().strftime('%d/%m/%Y'),
            'DUREE': employee_data.get('duree', 'غير محددة')
        }

        if employee_data['type_contrat'] == "CDD" and data.get('DPERIODE') != "غير محدد" and data.get(
                'FPERIODE') != "غير محدد":
            try:
                debut = datetime.datetime.strptime(data['DPERIODE'], "%Y-%m-%d")
                fin = datetime.datetime.strptime(data['FPERIODE'], "%Y-%m-%d")
                delta = fin - debut
                months = delta.days // 30
                days = delta.days % 30
                data['DUREE'] = f"{months} شهرا" + (f" و {days} يوما" if days else "")
            except (ValueError, TypeError) as e:
                print(f"Error calculating DUREE: {str(e)}")
                data['DUREE'] = "غير محددة"

        # Log genre and type_contrat before template selection
        print(
            f"Generating contract with genre: '{employee_data.get('genre')}', type_contrat: '{employee_data.get('type_contrat')}'")
        template = self.select_contract_template(employee_data['genre'], employee_data['type_contrat'])
        if not template:
            raise ValueError("No contract template found for the given genre and contract type")

        contrat_text = template
        for placeholder, value in data.items():
            contrat_text = contrat_text.replace(f'{{{{{placeholder}}}}}', str(value))

        return contrat_text

    def save_and_generate(self):
        try:
            required_fields = {
                'nom': self.get_widget_value(self.entries['nom']),
                'prenom': self.get_widget_value(self.entries['prenom']),
                'date_debut': self.get_widget_value(self.contract_entries['date_debut']),
                'salaire': self.get_widget_value(self.contract_entries['salaire']),
                'prime': self.get_widget_value(self.contract_entries['prime'])
            }

            for field, value in required_fields.items():
                if not value:
                    Messagebox.show_error(f"Le champ {field} est obligatoire", "Erreur")
                    return

            matricule = self.entries['matricule'].get().strip()
            if not matricule.isdigit():
                Messagebox.show_error("Le matricule doit contenir uniquement des chiffres", "Erreur")
                return



            # Vérifier si le matricule existe déjà
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM employees WHERE matricule = %s", (matricule,))
                if cursor.fetchone():
                    Messagebox.show_error(f"Le matricule {matricule} existe déjà", "Erreur")
                    return
            employee_data = {
                'matricule': matricule,
                'nom': required_fields['nom'],
                'prenom': required_fields['prenom'],
                'genre': self.variables["genre"].get(),
                'date_naissance': self.get_widget_value(self.entries['date_naissance']) or None,
                'lieu_naissance': self.get_widget_value(self.entries['lieu_naissance']) or None,
                'adresse': self.get_widget_value(self.entries['adresse']) or None,
                'ville': self.get_widget_value(self.entries['ville']) or "المحرس",
                'code_postal': self.get_widget_value(self.entries['code_postal']) or None,
                'cin': self.get_widget_value(self.entries['cin']) or None,
                'date_cin': self.get_widget_value(self.entries['date_cin']) or None,
                'lieu_cin': self.get_widget_value(self.entries['lieu_cin']) or "تونس",
                'poste': self.get_widget_value(self.entries['poste']) or None,
                'email': self.get_widget_value(self.entries['email']) or None,
                'telephone': self.get_widget_value(self.entries['telephone']) or None,
                'type_contrat': self.variables["contract_type"].get(),
                'date_debut': required_fields['date_debut'],
                'date_fin': self.get_widget_value(self.contract_entries['date_fin']) if self.variables[
                                                                                            "contract_type"].get() == "CDD" else None,
                'salaire_base': float(required_fields['salaire']),
                'prime': float(required_fields['prime']),
                'salary_type': self.variables["salary_type"].get(),
                'date_embauche': self.get_widget_value(self.entries['date_embauche']) or None,
                'dcon': self.get_widget_value(self.entries['dcon']) or None,
                'duree': self.get_widget_value(self.entries['duree']) or None,
                'atelier': self.get_widget_value(self.entries['atelier']) or None,
                'nbre_eche': self.get_widget_value(self.entries['nbre_eche']) or None,
                'fperiode': self.get_widget_value(self.entries['fperiode']) or None,
                'degre_polyvalence': self.get_widget_value(self.entries['degre_polyvalence']) or None
            }

            try:
                datetime.datetime.strptime(employee_data['date_debut'], "%Y-%m-%d")
                if employee_data['date_fin']:
                    datetime.datetime.strptime(employee_data['date_fin'], "%Y-%m-%d")
                    debut = datetime.datetime.strptime(employee_data['date_debut'], "%Y-%m-%d")
                    fin = datetime.datetime.strptime(employee_data['date_fin'], "%Y-%m-%d")
                    if fin <= debut:
                        Messagebox.show_error("La date de fin doit être après la date de début", "Erreur")
                        return
            except ValueError:
                Messagebox.show_error("Format de date invalide (AAAA-MM-JJ attendu)", "Erreur")
                return

            contrat_text = self.generate_contract_from_data(employee_data)

            with self.conn.cursor() as cursor:
                cursor.execute('''
                               INSERT INTO employees (matricule, nom, prenom, genre, date_naissance, lieu_naissance,
                                                      adresse, ville, code_postal, cin, date_cin, lieu_cin, poste,
                                                      email, telephone, type_contrat, date_debut, date_fin,
                                                      salaire_base, prime, salary_type, date_embauche, dcon,
                                                      duree, atelier, nbre_eche, fperiode, degre_polyvalence)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               ''', (
                                   employee_data['matricule'],
                                   employee_data['nom'],
                                   employee_data['prenom'],
                                   employee_data['genre'],
                                   employee_data['date_naissance'],
                                   employee_data['lieu_naissance'],
                                   employee_data['adresse'],
                                   employee_data['ville'],
                                   employee_data['code_postal'],
                                   employee_data['cin'],
                                   employee_data['date_cin'],
                                   employee_data['lieu_cin'],
                                   employee_data['poste'],
                                   employee_data['email'],
                                   employee_data['telephone'],
                                   employee_data['type_contrat'],
                                   employee_data['date_debut'],
                                   employee_data['date_fin'],
                                   employee_data['salaire_base'],
                                   employee_data['prime'],
                                   employee_data['salary_type'],
                                   employee_data['date_embauche'],
                                   employee_data['dcon'],
                                   employee_data['duree'],
                                   employee_data['atelier'],
                                   int(employee_data['nbre_eche']) if employee_data['nbre_eche'] else None,
                                   employee_data['fperiode'],
                                   employee_data['degre_polyvalence']
                               ))

                cursor.execute('''
                               INSERT INTO contrats (matricule, texte_contrat, date_creation, type_contrat)
                               VALUES (%s, %s, CURDATE(), %s)
                               ''', (
                                   employee_data['matricule'],
                                   contrat_text,
                                   employee_data['type_contrat']
                               ))

                self.conn.commit()

            self.current_employee = employee_data
            self.contract_text.config(state=tk.NORMAL)
            self.contract_text.delete(1.0, tk.END)
            self.contract_text.insert(tk.END, contrat_text, 'rtl')
            self.contract_text.config(state=tk.DISABLED)
            self.notebook.select(2)

            self.load_data()
            self.clear_form()
            self.status_var.set(f"Contrat {employee_data['type_contrat']} enregistré (N°{matricule})")
            Messagebox.show_info(f"Contrat {matricule} enregistré avec succès", "Succès")

        except pymysql.MySQLError as e:
            self.conn.rollback()
            Messagebox.show_error(f"Erreur SQL: {str(e)}", "Erreur DB")
        except ValueError as e:
            Messagebox.show_error(f"Erreur de valeur: {str(e)}", "Erreur")
        except Exception as e:
            Messagebox.show_error(f"Erreur inattendue: {str(e)}", "Erreur")



    def load_employee_table(self):

        with self.conn.cursor() as cursor:
            cursor.execute('''
                           SELECT matricule,
                                  nom,
                                  prenom,
                                  genre,
                                  date_naissance,
                                  lieu_naissance,
                                  adresse,
                                  ville,
                                  cin,
                                  date_cin,
                                  lieu_cin,
                                  poste,
                                  email,
                                  telephone,
                                  type_contrat,
                                  date_debut,
                                  date_fin,
                                  salaire_base,
                                  prime,
                                  salary_type
                           FROM employees
                           ''')
            self.update_table_data(cursor.fetchall())

    def generate_and_show_contract(self):
        try:
            if not self.current_employee:
                Messagebox.show_warning("Aucun employé sélectionné", "Attention")
                return

            # Vérifier si un contrat existe déjà pour cet employé
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM contrats WHERE matricule = %s",
                               (self.current_employee['matricule'],))
                if cursor.fetchone()[0] > 0:
                    # Si contrat existe déjà, demander confirmation pour regénérer
                    if not Messagebox.yesno("Un contrat existe déjà. Voulez-vous le regénérer ?",
                                            "Confirmation"):
                        return

            # Générer le nouveau contrat
            contrat_text = self.generate_contract_from_data(self.current_employee)

            with self.conn.cursor() as cursor:
                # Supprimer l'ancien contrat s'il existe
                cursor.execute("DELETE FROM contrats WHERE matricule = %s",
                               (self.current_employee['matricule'],))

                # Insérer le nouveau contrat
                cursor.execute("""
                               INSERT INTO contrats
                                   (matricule, date_creation, texte_contrat, type_contrat)
                               VALUES (%s, NOW(), %s, %s)
                               """, (
                                   self.current_employee['matricule'],
                                   contrat_text,
                                   self.current_employee['type_contrat']
                               ))
                self.conn.commit()

            # Afficher le contrat
            self.contract_text.config(state=tk.NORMAL)
            self.contract_text.delete(1.0, tk.END)
            self.contract_text.insert(tk.END, contrat_text, 'rtl')
            self.contract_text.config(state=tk.DISABLED)
            self.notebook.select(2)
            self.status_var.set("Contrat généré avec succès")

        except pymysql.Error as e:
            self.conn.rollback()
            Messagebox.show_error(f"Erreur MySQL: {str(e)}", "Erreur")
        except Exception as e:
            Messagebox.show_error(f"Erreur inattendue: {str(e)}", "Erreur")

    def update_table_data(self, rows):
        self.employee_table.delete_rows()
        today = datetime.datetime.now().date()

        for row in rows:
            matricule = row[0]
            action_frame = ttk.Frame(self.employee_table.view)

            # Vérifier si le contrat expire bientôt
            warning = ""
            if row[16]:  # Si date_fin existe
                try:
                    # Si c'est déjà un objet date
                    if isinstance(row[16], datetime.date):
                        end_date = row[16]
                    # Si c'est une chaîne de caractères
                    elif isinstance(row[16], str):
                        end_date = datetime.datetime.strptime(row[16], "%Y-%m-%d").date()
                    else:
                        end_date = None

                    if end_date:
                        days_left = (end_date - today).days
                        if 0 <= days_left <= 30:
                            warning = "⚠️ "  # Ajouter un emoji d'avertissement
                except (ValueError, TypeError):
                    pass

            ttk.Button(action_frame, text="Modifier",
                       command=lambda m=matricule: self.edit_employee(m),
                       bootstyle=(PRIMARY, OUTLINE), width=8).pack(side=LEFT, padx=2)
            ttk.Button(action_frame, text="Contrat",
                       command=lambda m=matricule: self.view_contract_from_table(m),
                       bootstyle=(INFO, OUTLINE), width=8).pack(side=LEFT, padx=2)

            # Ajouter l'avertissement au nom si nécessaire
            display_row = list(row[:14])
            display_row[1] = warning + display_row[1]  # Ajouter l'avertissement au nom

            display_row += [
                row[14] or "N/A",
                row[15].strftime("%Y-%m-%d") if isinstance(row[15], datetime.date) else (row[15] or "N/A"),
                row[16].strftime("%Y-%m-%d") if isinstance(row[16], datetime.date) else (row[16] or "N/A"),
                str(row[17]) if row[17] is not None else "N/A",
                str(row[18]) if row[18] is not None else "N/A",
                row[19] or "N/A",
                action_frame
            ]
            self.employee_table.insert_row(values=display_row)

        self.update_summary()

    def search_employee(self):
        matricule = self.variables["matricule"].get()
        if not matricule:
            Messagebox.show_warning("Veuillez saisir un matricule", "Attention")
            return

        try:
            with self.conn.cursor() as cursor:
                cursor.execute('''
                               SELECT matricule,
                                      nom,
                                      prenom,
                                      genre,
                                      DATE_FORMAT(date_naissance, '%%d/%%m/%%Y') as date_naissance,
                                      lieu_naissance,
                                      adresse,
                                      ville,
                                      cin,
                                      DATE_FORMAT(date_cin, '%%d/%%m/%%Y')       as date_cin,
                                      lieu_cin,
                                      poste,
                                      email,
                                      telephone,
                                      type_contrat,
                                      DATE_FORMAT(date_debut, '%%d/%%m/%%Y')     as date_debut,
                                      DATE_FORMAT(date_fin, '%%d/%%m/%%Y')       as date_fin,
                                      salaire_base,
                                      prime,
                                      salary_type
                               FROM employees
                               WHERE matricule = %s
                               ''', (matricule,))
                employee = cursor.fetchone()

            if employee:
                # Conversion explicite en dictionnaire
                employee_dict = {
                    'matricule': employee[0],
                    'nom': employee[1],
                    'prenom': employee[2],
                    'genre': employee[3],
                    'date_naissance': employee[4],
                    'lieu_naissance': employee[5],
                    'adresse': employee[6],
                    'ville': employee[7],
                    'cin': employee[8],
                    'date_cin': employee[9],
                    'lieu_cin': employee[10],
                    'poste': employee[11],
                    'email': employee[12],
                    'telephone': employee[13],
                    'type_contrat': employee[14],
                    'date_debut': employee[15],
                    'date_fin': employee[16],
                    'salaire_base': float(employee[17]) if employee[17] else 0.0,
                    'prime': float(employee[18]) if employee[18] else 0.0,
                    'salary_type': employee[19]
                }

                self.current_employee = employee_dict
                # Afficher les informations
                info_text = f"""Matricule: {employee[0]}
    Nom: {employee[1]} {employee[2]}
    Genre: {employee[3]}
    Date Naissance: {employee[4] or 'N/A'} à {employee[5] or 'N/A'}
    Adresse: {employee[6] or 'N/A'}, {employee[7] or 'N/A'}
    CIN: {employee[8] or 'N/A'} (délivré le {employee[9] or 'N/A'} à {employee[10] or 'N/A'})
    Poste: {employee[11] or 'N/A'}
    Email: {employee[12] or 'N/A'}
    Téléphone: {employee[13] or 'N/A'}
    Type Contrat: {employee[14] or 'N/A'}
    Date Début: {employee[15] or 'N/A'}
    Date Fin: {employee[16] or 'N/A'}
    Salaire Base: {employee[17] or 'N/A'} TND
    Prime: {employee[18] or 'N/A'} TND
    Type Salaire: {employee[19] or 'N/A'}"""

                self.info_text.config(state=tk.NORMAL)
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, info_text)
                self.info_text.config(state=tk.DISABLED)

                # Activer les boutons
                self.generate_contract_btn.config(state=tk.NORMAL)
                self.edit_btn.config(state=tk.NORMAL)
                self.delete_btn.config(state=tk.NORMAL)

                self.status_var.set(f"Employé trouvé: {employee[1]} {employee[2]}")
            else:
                self.clear_search()
                Messagebox.show_info("Aucun employé trouvé avec ce matricule", "Information")

        except Exception as e:
            self.clear_search()
            Messagebox.show_error(f"Erreur lors de la recherche: {str(e)}", "Erreur")
            self.status_var.set("Erreur de recherche")

    def clear_search(self):
        self.info_text.delete(1.0, tk.END)
        self.current_employee = None
        self.generate_contract_btn.config(state=DISABLED)
        self.status_var.set("Aucun résultat")

    def check_employee_data(self, matricule):
        """Version corrigée avec gestion robuste des dates"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM employees WHERE matricule = %s", (matricule,))
                employee = cursor.fetchone()

                if not employee:
                    return {"status": "error", "message": "Employé non trouvé"}

                # Conversion en dictionnaire si tuple
                if isinstance(employee, tuple):
                    cols = [col[0] for col in cursor.description]
                    employee = dict(zip(cols, employee))

                # Vérification des champs obligatoires
                required_fields = [
                    'matricule', 'nom', 'prenom', 'genre',
                    'type_contrat', 'date_debut', 'salaire_base'
                ]
                missing = [f for f in required_fields if not employee.get(f)]

                # Vérification des formats de date
                date_errors = []
                date_fields = {
                    'date_naissance': "%Y-%m-%d",
                    'date_cin': "%Y-%m-%d",
                    'date_debut': "%Y-%m-%d",
                    'date_fin': "%Y-%m-%d"
                }

                for field, fmt in date_fields.items():
                    if field in employee and employee[field]:
                        try:
                            datetime.datetime.strptime(str(employee[field]), fmt)
                        except ValueError:
                            date_errors.append(field)

                return {
                    "status": "success",
                    "data": employee,
                    "missing_fields": missing,
                    "date_errors": date_errors  # Toujours retourner cette clé
                }

        except Exception as e:
            return {"status": "error", "message": str(e), "missing_fields": [], "date_errors": []}

    def diagnose_database(self):
        """Génère un rapport complet sur l'état des données"""
        try:
            with self.conn.cursor() as cursor:
                # 1. Statistiques de base
                cursor.execute("SELECT COUNT(*) FROM employees")
                total_employees = cursor.fetchone()[0]

                cursor.execute("""
                               SELECT COUNT(*)                                              as total,
                                      SUM(CASE WHEN type_contrat = 'CDD' THEN 1 ELSE 0 END) as cdd_count,
                                      SUM(CASE WHEN type_contrat = 'CDI' THEN 1 ELSE 0 END) as cdi_count,
                                      SUM(CASE WHEN date_fin IS NULL THEN 1 ELSE 0 END)     as no_end_date
                               FROM employees
                               """)
                stats = cursor.fetchone()

                # 2. Problèmes courants
                cursor.execute("""
                               SELECT COUNT(*)                as missing_essential,
                                      GROUP_CONCAT(matricule) as samples
                               FROM employees
                               WHERE matricule IS NULL
                                  OR nom IS NULL
                                  OR prenom IS NULL
                                  OR type_contrat IS NULL
                                  OR date_debut IS NULL LIMIT 5
                               """)
                problems = cursor.fetchone()

                return {
                    "total_employees": total_employees,
                    "cdd_count": stats[1],
                    "cdi_count": stats[2],
                    "no_end_date": stats[3],
                    "missing_essential": problems[0],
                    "problem_samples": problems[1] or "Aucun"
                }

        except Exception as e:
            return {"error": str(e)}






if __name__ == "__main__":
    app = ContratApplication(ttk.Window())
    app.root.mainloop()