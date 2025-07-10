import random
import tkinter as tk
from tkinter import messagebox

questions_data = [
    ("La fase de planeamiento abarca solamente los sectores de la empresa involucrados en los futuros proyectos.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿Cuál de los siguientes motivos no forma parte de los motivos por los cuales, según el Standish Group, fallan los proyectos informáticos?", ["Objetivos poco claros", "Especificaciones incompletas", "Incompetencia tecnológica", "Expectativas no realistas", "Renuncia de los usuarios a utilizar la tecnología implementada", "Cronogramas irreales"], "Renuncia de los usuarios a utilizar la tecnología implementada"),
    ("¿Cuál de los siguientes objetivos no corresponde a los objetivos de la fase de planeamiento?", ["Establecer la estrategia de Hardware y Software", "Identificar mejoras concretas a las aplicaciones existentes", "Contratar los componentes de Tecnología informática necesarios"], "Contratar los componentes de Tecnología informática necesarios"),
    ("Un desarrollador puede aprender rápidamente uno de los lenguajes de programación de propósito general vigentes al momento, aunque debe atravesar una curva de aprendizaje.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Un cliente delgado es un dispositivo que permite que un usuario utilice una máquina virtual.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("La contraseña es un elemento que:", ["No debe cambiarse bajo ningún aspecto", "Habilita una funcionalidad a una persona", "Verifica la autenticidad de un individuo"], "Verifica la autenticidad de un individuo"),
    ("¿Cuál de los siguientes elementos no es un componente de una base de datos?", ["Software", "Datos", "Computadora", "Concentrador de comunicaciones", "Usuarios"], "Concentrador de comunicaciones"),
    ("¿Cuál de los siguientes elementos no corresponden a 'Agujeros' en la seguridad de la información?", ["Emocionales", "Físicos", "Comportamiento humano"], "Emocionales"),
    ("¿Cuál de las siguientes ventajas no corresponden a las ventajas de adquirir una aplicación por paquete?", ["Costo", "Mejores prácticas", "Funcionalidad flexible", "Evolución de actualizaciones periódicas", "Menor tiempo de start-up"], "Funcionalidad flexible"),
    ("El comportamiento de un sistema es una narración que describe la reacción de un sistema dado a una determinada situación.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("La tecnología de duplicación de discos permite protegernos de la pérdida de información frente a un incendio en nuestros servidores.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("¿Cuál de las siguientes áreas NO corresponde a un área fundamental del software?", ["Software Social", "Utilitarios", "Lenguajes de programación", "Sistemas Operativos", "Productos Financieros"], "Productos Financieros"),
    ("¿Cuál de las opciones no corresponde a un periférico de un sistema de cómputos?", ["Sensor de temperatura", "Procesador", "Lector de huellas digitales", "Monitor"], "Procesador"),
    ("¿Cuál de las siguientes áreas no corresponde a una de las definidas en las normas internacionales de seguridad de la información?", ["Administración Financiera", "Continuidad de operaciones", "Desarrollo y mantenimiento de aplicaciones", "Clasificación y control de activos"], "Administración Financiera"),
    ("¿Cuál de los siguientes usos no corresponde a los de un sistema de información?", ["Ser el registro cronológico del suceso de una organización", "Apoyar los procesos de mejora continua dentro de una organización"], "Ser el registro cronológico del suceso de una organización"),
    ("El principio por el cual las computadoras deben buscar aumentar el intelecto humano fue propuesto por el Dr. Engelbart a principio de la década de los noventa.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Un riesgo es un evento incierto, que, en casos de ocurrir, provocará un exceso de los gastos previstos en un proyecto.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Una hoja de riesgo permite enumerar todos los riesgos posibles a los cuales se puede enfrentar un proyecto.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Las alternativas de formulación de planes informáticos son dos: 1. Conjunta. 2. Disociada.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Un ERP es: Un producto de software que cubre todas las operaciones de la compañía.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Hacer un estudio de un sistema es comprender el funcionamiento de un sistema desde el punto de vista de las personas que lo utilizan.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Los servicios de consultoría que se adquieren con la licencia del ERP permiten parametrizarlo a las necesidades de la empresa que lo ha adquirido.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Los sistemas de información estratégicos se orientan básicamente a la automatización/sistematización de procesos internos.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿A qué llamamos hardware?", ["Dispositivos y Electrónica", "Toda la parte física, que se puede ver y tocar de una computadora"], "Toda la parte física, que se puede ver y tocar de una computadora"),
    ("CSCW es:", [ "La disciplina que estudia las formas en las que la gente trabaja en equipo, con la tecnología que lo facilita", "Un lenguaje de programación utilizado para el análisis de datos colaborativos", "Un protocolo de comunicación para redes inalámbricas seguras", "Un sistema operativo especializado en servidores de colaboración"],"La disciplina que estudia las formas en las que la gente trabaja en equipo, con la tecnología que lo facilita"),
    ("El software de apoyo al usuario denominado Microsoft Office 365 es una aplicación representativa de lo que se llama:", ["Software como servicio"], "Software como servicio"),
    ("La tecnología Hot-Swap permite reemplazar componentes dañados de un sistema reflejado sin necesidad de detener su funcionamiento.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Los sistemas de apoyo a las decisiones son un conjunto de programas y herramientas que permiten registrar detalladamente las operaciones de la empresa.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Indique una de las características del conocimiento.", ["Tácito","Digitalizado automáticamente", "Completamente objetivo en todos los casos", "Se genera exclusivamente por medios tecnológicos"],"Tácito"),
    ("¿Cuál de los siguientes criterios no forman parte de los criterios de selección de proyectos informáticos identificados durante la fase de Planeamiento?", ["Plazo de ejecución", "Económico", "Costo / Beneficio", "Cercanía con el proveedor", "Apoyo directivo"], "Cercanía con el proveedor"),
    ("Las tareas de la fase de planeamiento se pueden agrupar en Creativas y de Formalización.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Desde el punto de vista de la gestión de IT en una organización una aplicación es una pieza de software que brinda información para la toma de decisiones.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Los FCE sirven para identificar métricas utilizables en una organización.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El groupware es:", ["Grupo de dispositivos que se conectan a una computadora", "Grupo de tecnologías que sirven para apoyar las tareas de un usuario", "Sistema informático que agrupa un conjunto de personas en una tarea común", "Grupo de redes sociales que un usuario utiliza", "Grupo de tecnologías asociadas que pueden ser utilizadas en una computadora"], "Sistema informático que agrupa un conjunto de personas en una tarea común"),
    ("El sistema de detección es un componente de las redes de comunicaciones.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿Cuál de los siguientes elementos no son utilizados para controlar el adecuado uso de los recursos?", ["Perfil", "Grupos", "Usuario", "Contraseña", "Barrera automática"], "Barrera automática"),
    ("¿Cuál de los siguientes ejes no forman parte de las alternativas estratégicas?", ["Información común", "Globalización", "Procesos de Información", "Nuevos Mercados", "Contenido de la información"], "Globalización"),
    ("La revisión y aprobación gerencial del plan informático no es necesario realizarlo en todas las organizaciones.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("¿Cuál de las siguientes respuestas no corresponde a una respuesta que se puede dar a un riesgo?", ["Evitar", "Adquirir", "Transferir", "Mitigar", "Aceptar"], "Adquirir"),
    ("¿Cuál de los siguientes requisitos no corresponden a los requisitos de la información eficiente?", ["Comparabilidad", "Economía", "Elasticidad", "Utilidad", "Flexibilidad"], "Elasticidad"),
    ("¿Cuál de las siguientes características no corresponden a un sistema transaccional?", ["Se deben adquirir a un mismo proveedor", "Forma la plataforma informática", "Beneficios visibles y palpables", "Permiten ahorros significativos", "Justificación fácil frente a la dirección"], "Se deben adquirir a un mismo proveedor"),
    ("¿Cuál de las siguientes herramientas no corresponde a una herramienta de data mining?", ["Descubrimiento de reglas", "Adaptativos", "Texto to speech", "Clasificaciones", "Modelos funcionales"], "Texto to speech"),
    ("Una de las claves para el máximo responsable de la tecnología informática de una organización es 'planificar la utilización de la tecnología informática en el negocio'.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El perfil declara los derechos y restricciones de un usuario.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("La exposición a un riesgo se calcula contemplando su probabilidad de ocurrencia y su impacto.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Los tipos de datos son:", ["Referenciales: marco para los demás datos", "Transaccionales: reflejan las operaciones que se realizan en la empresa"], ["Referenciales: marco para los demás datos", "Transaccionales: reflejan las operaciones que se realizan en la empresa"]),
    ("La estructura de un sistema es la distribución de los elementos y su forma de interconexión.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Una línea directa digital es un servicio de comunicaciones que establece:", ["Conectar múltiples lugares con una oficina central", "Comunicación simultánea con internet y con una oficina remota", "Conexión de caudal fijo, constante y reservado por el proveedor", "Compartir un acceso a internet entre varias empresas", "Conexión a internet con ancho de banda variable"], "Conexión de caudal fijo, constante y reservado por el proveedor"),
    ("La sigla EDT de una herramienta utilizada en la gestión de proyectos significa 'Estructura de Distribución del Trabajo'.", ["VERDADERO", "FALSO"], "FALSO"),
    ("No es necesario que los proyectos tengan un documento de cierre.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿Cuál de las siguientes cualidades no son necesarias para un analista de sistemas?", ["Automotivado", "Consultor", "Objetivo", "Analítico", "Comunicador", "Interrogador"], "Consultor"),
    ("¿Cuál de los siguientes elementos no corresponde a una de las funciones del Sistema operativo?", ["Ejecutar Software", "Administrar recursos", "Controlar el nivel de energía eléctrica del procesador", "Controlar los dispositivos y gestionar conflictos entre ellos", "Vigilar el funcionamiento general del sistema"], "Controlar el nivel de energía eléctrica del procesador"),
    ("¿Cómo se almacena la información en la memoria principal?", ["Como letras y números", "Con los números del 0 al 9", "En conjuntos de valores 0 o 1"], "En conjuntos de valores 0 o 1"),
    ("Un dato es un elemento descriptivo de un individuo u organización que sea de nuestro interés.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El código UNICODE es un código que traduce:", ["Más de 1024 caracteres a una secuencia de entre 8 a 64 dígitos binarios", "128 caracteres y símbolos a 7 dígitos binarios", "256 caracteres y símbolos a 8 dígitos binarios", "1024 caracteres y símbolos a 10 dígitos binarios", "512 caracteres y símbolos a 9 dígitos binarios"], "Más de 1024 caracteres a una secuencia de entre 8 a 64 dígitos binarios"),
    ("La minería de datos se refiere a la aplicación de métodos computacionales que permiten la obtención de conclusiones basadas en reglas de inferencia.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Un proyecto requiere de un objetivo a alcanzar contando un recurso finito y que se van negociando durante el desarrollo del proyecto.", ["VERDADERO", "FALSO"], "FALSO"),
    ("La racionalidad limitada implica simplificar la realidad.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("¿Cuál de las siguientes etapas no pertenece a las etapas de un proyecto?", ["Ejecución", "Inicio", "Contabilización", "Planificación", "Monitoreo"], "Contabilización"),
    ("Uno de los objetivos de la fase de instalación es crear la estructura necesaria para una eficiente operación de la aplicación informática en la organización.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Un sistema es:", ["Conjunto de elementos de información que nos permiten operar una organización", "Conjunto de procesos que interactúan con los diferentes sectores de una organización", "Conjunto de elementos interconectados para alcanzar un objetivo", "Conjunto de Datos y procesos aplicables a la empresa"], "Conjunto de elementos interconectados para alcanzar un objetivo"),
    ("La conversión de Shock es el proceso en el cual simultáneamente se están utilizando la aplicación informática que se dejaría de utilizar y la nueva aplicación informática que se está instalando.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Indicar en la secuencia correcta los tres tipos de pruebas que se debe realizar en forma previa a la puesta en marcha de una aplicación informática son:", ["Crear los procedimientos necesarios para la operación correcta del sistema", "Crear la estructura necesaria para una eficiente operación del sistema y entrenar a los usuarios que lo van a utilizar", "Efectuar la conversión más adecuada entre el nuevo sistema y el que existía anteriormente"], ["Crear los procedimientos necesarios para la operación correcta del sistema", "Crear la estructura necesaria para una eficiente operación del sistema y entrenar a los usuarios que lo van a utilizar", "Efectuar la conversión más adecuada entre el nuevo sistema y el que existía anteriormente"]),
    ("Los elementos de un sistema son su estructura y su comportamiento.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("En la tarea de situación actual de la fase de planeamiento se deben evaluar las condiciones del mercado en el cual la organización actúa.", ["VERDADERO", "FALSO"], "FALSO"),
    ("En la tarea de requerimientos funcionales se realiza el estudio detallado de las necesidades de información de todos los sectores participantes en la aplicación.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Las especificaciones pueden ser funcionales o técnicas.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Los informes que se deben realizar en la fase de planeamiento son:", ["Diagnóstico", "Propuesta de Capacitación", "Plan de Sistemas", "Plan de adquisiciones"], ["Diagnóstico", "Plan de Sistemas"]),
    ("La información son datos dotados de pertinencia y propósito.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El código ASCII utilizado en la mayoría de las computadoras actuales es un código que traduce:", ["256 caracteres y símbolos a 8 dígitos binarios", "Más de 1024 caracteres a una secuencia de entre 8 a 64 dígitos binarios", "512 caracteres y símbolos a 9 dígitos binarios", "1024 caracteres y símbolos a 10 dígitos binarios", "126 caracteres y símbolos a 7 dígitos binarios"], "256 caracteres y símbolos a 8 dígitos binarios"),
    ("Los componentes de la unidad central de proceso son:", ["Memoria, procesador y teclado", "Procesador, teclado y mouse", "Procesador, monitor y teclado", "Memoria principal, procesador, y Controladores de E/S", "Memoria principal, procesador y disco"], "Memoria principal, procesador, y Controladores de E/S"),
    ("¿Qué concepto se conoce como Cloud Computing?", ["Tecnología que permitirá ofrecer a los usuarios finales una computadora virtual que podrá utilizar desde cualquier lugar conectado a Internet y dimensionada en forma dinámica", "Sistema operativo que se ejecuta sin necesidad de conexión a Internet", "Dispositivo de almacenamiento portátil de gran capacidad", "Software utilizado para proteger redes inalámbricas domésticas"], "Tecnología que permitirá ofrecer a los usuarios finales una computadora virtual que podrá utilizar desde cualquier lugar conectado a Internet y dimensionada en forma dinámica"),   
    ("¿Qué es data Mining?",[ "Método para descubrir conocimiento en las redes", "Técnica para limpiar discos duros y liberar espacio", "Sistema de compresión de archivos en la nube", "Algoritmo que bloquea el acceso a datos no autorizados"], "Método para descubrir conocimiento en las redes"),
    ("Los permisos por función indican:", ["Las autorizaciones para usar el ERP", "Las ventajas que permiten el uso del ERP", "Las funciones que se encuentran disponibles en ERP", "Las funciones del ERP que tienen disponibles cada usuario"], "Las funciones del ERP que tienen disponibles cada usuario"),
    ("Un datawarehouse es un software que se utiliza para administrar los datos de un centro de distribución de una empresa.", ["VERDADERO", "FALSO"], "FALSO"),
    ("El lenguaje ABAP permite incorporar funcionalidad en SAP.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Medición es el proceso por el cual se asignan números o símbolos a los atributos de las entidades del mundo real.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Los interesados en un proyecto se deben clasificar contemplando dos ejes, el poder dentro de la organización y el conocimiento de la tecnología informática que poseen.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("La técnica de la observación directa utilizada para la tarea de requerimientos funcionales es utilizada para preguntarle pocas cosas a mucha gente en poco tiempo.", ["VERDADERO", "FALSO"], "FALSO"),
    ("El líder de proyectos informáticos debe ser el facilitador de la gestión de esos proyectos.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("En la tarea de Análisis del estado actual de la fase de mantenimiento corresponde realizar un análisis de la utilidad de las herramientas informáticas de la organización para el adecuado cumplimiento de sus objetivos.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El outsourcing es el proceso por el cual un proveedor ofrece servicios de consultoría a la organización.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Probabilidad de obtener ese rendimiento estimado:", ["La tasa de interés futura estimada", "La tasa de depreciación", "La tasa de conversión", "Ningún otro elemento"], "La tasa de interés futura estimada"),
    ("¿Cuál es la tipología de redes locales más confiable?", ["Estrella", "Barra", "Anillo"], "Estrella"),
    ("La comunicación telefónica tradicional utiliza el sistema de conmutación por paquete.", ["VERDADERO", "FALSO"], "FALSO"),
    ("La conversión en paralelo es el proceso por el cual en un mismo momento se deja de utilizar una aplicación informática y se comienza a utilizar la aplicación informática que se instala.", ["VERDADERO", "FALSO"], "FALSO"),
    ("La arquitectura de aplicaciones es un gráfico en el cual se representan todas las aplicaciones que la organización necesita para sus operaciones junto con los principales datos que se comparten entre ellas.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Calidad de Software: Concordancia con los requisitos (especificaciones) funcionales y de rendimiento explícitamente establecidos.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Una falla es cualquier falta de concordancia con las especificaciones implícitas generalmente establecidas.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Las copias de seguridad diferenciales ocupan más espacio que las incrementales.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Si un componente de software se comporta de una manera distinta a lo que indican las especificaciones del producto es una:", ["Duda de calidad", "Falla de calidad"], "Falla de calidad"),
    ("El flujo de información se compone de información completa, información interna e información detallada.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("La conversión es el proceso por el cual se instruye a los usuarios de la aplicación en su uso.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Las siglas de la herramienta DFD significan 'Diseño Flotante Distribuido'.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Uno de los objetivos de la fase de mantenimiento es identificar los posibles cambios a realizar en las aplicaciones que se encuentran funcionando en la organización.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("¿Cuál de los siguientes elementos no es un objetivo de la fase de Diseño?", ["Identificar exactamente todos los elementos participantes en el sistema", "Identificar totalmente las necesidades de información", "Establecer una organización capaz de poner en marcha la aplicación", "Crear una aplicación informática confiable"], "Crear una aplicación informática confiable"),
    ("El congelamiento que se menciona en la tarea de revisión gerencial de la fase de Diseño se refiere a:", ["Cierre de los tiempos de entrega de los componentes con los proveedores de la aplicación a poner en marcha", "Cierre de los precios pactados con los diversos proveedores de la aplicación a poner en marcha", "Cierre de los posibles cambios a las especificaciones funcionales y técnicas de la aplicación a poner en marcha"], "Cierre de los posibles cambios a las especificaciones funcionales y técnicas de la aplicación a poner en marcha"),
    ("Indique las ventajas del alquiler de equipamiento informático:", ["Poca inversión inicial", "Ventaja impositiva", "Riesgo de equivocación", "Inversión inicial importante", "Problemas con el reciclado", "Evita obsolescencia", "Mayor costo total", "El proveedor se responsabiliza del funcionamiento"], ["Poca inversión inicial", "Ventaja impositiva", "Evita obsolescencia", "El proveedor se responsabiliza del funcionamiento"]),
    ("El fenómeno conocido como 'Depresión post-ERP', se refiere a:", ["Falta de participación de los directivos", "Desatención de los colaboradores por la participación en las actividades de capacitación", "Problemas en la nueva forma de operar", "Excesivo costo de licenciamiento y mantenimiento anual", "Horas no contempladas en la implementación"], "Problemas en la nueva forma de operar"),
    ("Las etapas de una entrevista son: preparación desarrollo e informe.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Las copias de seguridad en internet deben estar permanentemente conectadas a la infraestructura para garantizar la seguridad de los datos.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Los elementos que se deben verificar en las pruebas previstas a la puesta en marcha de una aplicación informática son:", ["Aplicabilidad y Eficacia"], "Aplicabilidad y Eficacia"),
    ("¿Cuál de las siguientes aplicaciones no son de técnicas de data mining?", ["Atención de clientes", "Análisis de riesgo crediticio", "Text mining", "Detección de Fraudes", "Clasificación de grupos"], "Atención de clientes"),
    ("El conocimiento es información valiosa la cual ha sido sometida a un proceso de verificación y confirmación.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Las interfases hombre / máquina se describen en el diseño funcional.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Un certificado digital asegura la identidad del emisor de un mensaje.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("En el ámbito de las aplicaciones empresariales, si un programa falla frecuentemente es de:", ["Regular calidad", "Dudosa calidad", "Depende de otros factores vinculados a la calidad", "Baja calidad"], "Baja calidad"),
    ("Las soluciones por industria:", ["Proveen mecanismos especiales de funcionamiento", "Ajustan la información para cada tipo de industria", "Permiten ajustar el ERP de una empresa de determinada actividad", "Entregan información específica para cada industria"], "Permiten ajustar el ERP de una empresa de determinada actividad"),
    ("El analista técnico debe documentar los procesos de negocios que se realizan en la organización.", ["VERDADERO", "FALSO"], "FALSO"),
    ("A un hacker le resulta más sencillo explotar una falla en el firewall de la empresa que un comportamiento humano con actitud relajada hacia la seguridad de la información.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿Cuál de los siguientes tipos de costos no es un costo visible de la incorporación de un ERP en la empresa?", ["Equipamiento", "Servicios de Implementación y puesta en marcha", "Servicios de promoción y publicidad", "Capacitación y consultoría", "Licencia inicial de Software"], "Servicios de promoción y publicidad"),
    ("El objetivo de una red de información compartida es que cada miembro de la organización conozca la tarea que debe realizar y sus responsabilidades en la organización.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("¿Cuál de los siguientes no corresponde a un componente de base de datos?", ["Software", "Datos", "Computadora", "Concentrador de comunicaciones", "Usuarios"], "Concentrador de comunicaciones"),
    ("Las cuatro fases de nuestra metodología son Planeamiento, análisis y diseño, adquisición, y mantenimiento.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿Cuál de los siguientes principios no corresponde a los principios de la medición?", ["Análisis", "Formulación", "Recolección", "Interpretación", "Agrupación", "Retroalimentación"], "Agrupación"),
    ("¿Cuál de los siguientes motivos no es uno de los que permiten justificar el cambio de un ERP?", ["Mejorar la gestión financiera", "Acelerar la línea de producción de la fabrica", "Flexibilidad", "Mejorar decisiones gerenciales", "Reducción de personal"], "Reducción de personal"),
    ("¿Cuál de las siguientes áreas del conocimiento no están involucradas en la disciplina de gestión de proyectos?", ["Calidad", "Riesgos", "Confiabilidad", "Comunicación"], "Confiabilidad"),
    ("En la tarea de Objetivos empresarios se debe identificar las tecnologías a utilizar en la organización.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿Cuál de los siguientes grupos de conocimientos no son los que debe asimilar un director de recursos informáticos?", ["Básicos", "Criptografía"], "Criptografía"),
    ("Un datawarehouse se abastece de fuentes de datos internas y externas.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Las tecnologías de la información son todas aquellas herramientas que permiten y dan soporte a los sistemas de información.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El protocolo IP utilizado en internet fue definido para:", ["Identificar los equipos que se encuentran conectados en internet", "Identificar los dispositivos con los cuales los usuarios se conectan a las redes sociales", "Permitir la transmisión de radios AM y FM por internet"], "Identificar los equipos que se encuentran conectados en internet"),
    ("La tecnología de la virtualidad se utiliza para que las empresas entreguen productos de forma virtual.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Las aplicaciones de apoyo al usuario buscan mejorar la productividad individual.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Open Office es un software para utilizar vía web.", ["VERDADERO", "FALSO"], "FALSO"),
    ("¿Cuál de los siguientes productos no son cloud?", ["Google documents", "Office 365", "Open office"], "Open office"),
    ("Una VPN es:", ["Una tecnología que permite montar una red para el tráfico privado de datos sobre una red pública"], "Una tecnología que permite montar una red para el tráfico privado de datos sobre una red pública"),
    ("En la fase de planeamiento se debe determinar los proveedores tecnológicos con los cuales la organización trabajará.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Un lenguaje de programación permite la comunicación entre aplicaciones de software.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Un sistema operativo es:", ["Un software que permite controlar las operaciones de la empresa", "Programas que facilitan la ejecución de los procesos y brindan una interfase estándar para en el uso del hardware"], "Programas que facilitan la ejecución de los procesos y brindan una interfase estándar para en el uso del hardware"),
    ("La cláusula CIR sirve para:", ["Aceptar una tasa de degradación del servicio"], "Aceptar una tasa de degradación del servicio"),
    ("Reconocimiento de una computadora: Por número (IP) y por nombre (DNS).", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El fenómeno conocido como 'Depresión post-ERP' se refiere a:", ["Falta de participación de los directivos", "Desatención de los colaboradores por la participación en las actividades de capacitación", "Problemas en la nueva forma de operar", "Excesivo costo de licenciamiento y mantenimiento anual", "Horas no contempladas en la implementación"], "Problemas en la nueva forma de operar"),
    ("Las etapas de una entrevista son: preparación, desarrollo e informe.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("¿Cuál de las siguientes aplicaciones no son de técnicas de data mining?", ["Atención de clientes", "Análisis de riesgo crediticio", "Text mining", "Detección de Fraudes", "Clasificación de grupos"], "Atención de clientes"),
    ("El conocimiento es información valiosa la cual ha sido sometida a un proceso de verificación y confirmación.", ["VERDADERO", "FALSO"], "FALSO"),
    ("En el ámbito de las aplicaciones empresariales, si un programa falla frecuentemente es de:", ["Regular calidad", "Dudosa calidad", "Depende de otros factores vinculados a la calidad", "Baja calidad"], "Baja calidad"),
    ("OLAP pone el foco en la velocidad de actualización.", ["VERDADERO", "FALSO"], "FALSO"),
    ("Principios de la medición son: FORMULACIÓN - RECOLECCION - ANALISIS -INTERPRETACION - RETROALIMENTACIÓN", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("El estudio de factibilidad de proyectos informáticos en la fase de planeamiento tiene un aspecto técnico, otro económico y el último un aspecto operacional.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("Medición es el proceso por el cual se asignan números o símbolos a los atributos de las entidades del mundo real.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("OLTP pone foco en la velocidad de actualización.", ["VERDADERO", "FALSO"], "VERDADERO"),
    ("¿Qué utilidad tienen las computadoras del top500?", ["Se ofrecen para que sean utilizados por diferentes empresas y/o instituciones", "Se utilizan exclusivamente para el entretenimiento y videojuegos de alto rendimiento", "Sirven como servidores de correo electrónico en redes empresariales pequeñas", "Se emplean únicamente para tareas administrativas rutinarias en oficinas gubernamentales"], "Se ofrecen para que sean utilizados por diferentes empresas y/o instituciones"),
    ("¿Cuál de los siguientes pasos no corresponde a los pasos del proceso de toma de decisiones en las empresas según Simon?", ["Inteligencia", "Comparación de puntos de vista", "Diseño", "Elección"], "Comparación de puntos de vista"),
    ("¿Cuál de los siguientes elementos no forman parte de los que requieren la aplicación de normas/procedimientos de seguridad de la información?", ["Uso de contraseñas", "Acceso a sistemas informáticos", "Accesos al edificio", "Respaldo de datos críticos"], "Accesos al edificio"),
    ("¿Cuál de los siguientes elementos no se incluyen en el documento de inicio del proyecto?", ["Requerimientos globales", "Propósito", "Conclusiones", "Hitos importantes", "Interesados"], "Conclusiones"),
    ("En la evaluación de las inversiones en IT, para evaluar el concepto debemos contemplar:", ["Rendimiento estimado", "Probabilidad de obtener ese rendimiento estimado", "La tasa de interés futura estimada", "La tasa de depreciación",  "La tasa de conversión", "Ningún otro elemento"] , "Rendimiento estimado"),
    ("¿Cuál de los siguientes elementos caracteriza a los representantes de los usuarios?", ["Difícil de encontrar", "Debe ser experto en informática", "Algunas metodologías se le dice Super Usuario", "Representante de sector"], "Representante de sector"),



]
class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cuestionario")
        self.score = 0
        self.current = 0
        self.questions = random.sample(questions_data, k=min(60, len(questions_data)))

        self.question_label = tk.Label(master, wraplength=600, font=('Arial', 14))
        self.question_label.pack(pady=20)

        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack()

        self.result_label = tk.Label(master, font=('Arial', 12))
        self.result_label.pack(pady=10)

        self.show_question()

    def show_question(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        if self.current >= len(self.questions):
            self.show_result()
            return

        q_text, options, _ = self.questions[self.current]
        self.question_label.config(text=f"{self.current + 1}. {q_text}")

        for opt in options:
            btn = tk.Button(self.buttons_frame, text=opt, wraplength=550, justify="left", bg='SystemButtonFace',

                            command=lambda selected=opt: self.check_answer(selected))
            btn.pack(pady=5)

    def check_answer(self, selected):
        q_text, options, correct = self.questions[self.current]
        for btn in self.buttons_frame.winfo_children():
            if btn['text'] == selected:
                if selected == correct:
                    btn.config(bg='green')
                    self.score += 1
                else:
                    btn.config(bg='red')
            elif btn['text'] == correct:
                btn.config(bg='green')

        self.master.after(1000, self.next_question)

    def next_question(self):
        self.current += 1
        self.show_question()

    def show_result(self):
        percent = (self.score / len(self.questions)) * 100
        for widget in self.master.winfo_children():
            widget.destroy()

        result_text = f"Obtuviste {self.score}/{len(self.questions)} respuestas correctas.\n\nPorcentaje: {percent:.2f}%"
        result_label = tk.Label(self.master, text=result_text, font=('Arial', 14))
        result_label.pack(pady=20)

        restart_button = tk.Button(self.master, text="Reiniciar", font=('Arial', 12), command=self.restart_quiz)
        restart_button.pack(pady=10)

    def restart_quiz(self):
        self.score = 0
        self.current = 0
        self.questions = random.sample(questions_data, k=min(40, len(questions_data)))
        for widget in self.master.winfo_children():
            widget.destroy()
        self.__init__(self.master)

def start_quiz():
    start_window.destroy()
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

start_window = tk.Tk()
start_window.title("Inicio del Quiz")
start_label = tk.Label(start_window, text="Bienvenido al Cuestionario", font=('Arial', 16))
start_label.pack(pady=20)
start_button = tk.Button(start_window, text="Iniciar", font=('Arial', 12), command=start_quiz)
start_button.pack(pady=10)
start_window.mainloop()