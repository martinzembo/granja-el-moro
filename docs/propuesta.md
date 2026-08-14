
1. Introducción
Granja "El Moro" es una empresa de producción avícola ubicada en la ciudad de Lobos, provincia de Buenos Aires. Su actividad principal consiste en la cría de pollos parrilleros para su posterior entrega a faena, contando con cinco galpones que permiten alojar hasta 119.000 aves por crianza.
Actualmente, la gestión operativa del establecimiento se apoya en procesos manuales: los granjeros envían por WhatsApp los datos diarios de cada galpón (mortandad, consumo de agua, alimento, gas y electricidad), y esa información es volcada manualmente en planillas de cálculo. Este esquema, si bien funcional en sus inicios, presenta limitaciones importantes en cuanto a la oportunidad, trazabilidad y confiabilidad de la información.
El presente documento constituye la propuesta de proyecto para el desarrollo de un sistema informático integrado que digitalice y centralice la gestión de crianzas de Granja "El Moro". El sistema permitirá a los granjeros registrar datos diarios desde una aplicación móvil, al tiempo que brindará al administrador un panel de monitoreo en tiempo real con alertas ante desvíos y el cálculo automatizado de los índices de rendimiento al cierre de cada crianza.
En las secciones siguientes se presenta la fundamentación del proyecto, sus objetivos y alcance, la metodología de desarrollo propuesta, el análisis de viabilidad, el cronograma estimado y las referencias consultadas.


2. Fundamentación
2.1 Por qué un sistema informático
La necesidad de contar con información precisa y oportuna durante el transcurso de una crianza es crítica para la toma de decisiones del administrador. Un desvío en el índice de mortandad o en el consumo de agua puede ser indicador temprano de una enfermedad o un desperfecto en las instalaciones; detectarlo a tiempo puede significar la diferencia entre intervenir a tiempo o perder un porcentaje significativo de aves.
El proceso actual —recolección por WhatsApp y volcado manual en planillas— introduce demoras y posibles errores de transcripción que reducen la confiabilidad de los datos. Un sistema informático elimina la intermediación manual, centraliza la información y habilita su análisis en tiempo real, funcionalidades que no son alcanzables con el esquema actual.
2.2 Stakeholders del desarrollo
Administrador de la granja (propietario): principal usuario del panel de monitoreo y destinatario de los reportes de cierre de crianza.
Granjeros: usuarios de la aplicación móvil para la carga diaria de datos operativos.
Empresa integradora / faena: receptor indirecto de los índices de rendimiento que determinan el precio por pollo entregado.
2.3 Necesidad no satisfecha
La situación actual presenta tres problemas concretos que el sistema viene a resolver:
Falta de trazabilidad: los datos históricos de crianzas anteriores no están consolidados en un repositorio único y estructurado, lo que dificulta el análisis comparativo y la identificación de patrones.
Demoras en la información: el circuito WhatsApp-planilla introduce una latencia que impide la detección temprana de desvíos durante la crianza.
Errores de volcado: el ingreso manual de datos a la planilla es susceptible a errores tipográficos que afectan la precisión de los indicadores calculados.
2.4 Situación actual y situación esperada
En la actualidad, el granjero envía un mensaje de WhatsApp por día con los datos de cada galpón. El administrador los recibe, los transcribe a una planilla de cálculo y calcula manualmente los índices de crecimiento y conversión. Al cierre de la crianza, consulta una tabla impresa de doble entrada para determinar el precio por pollo a facturar.
Con el sistema propuesto, el granjero ingresará los datos directamente desde su teléfono a través de una aplicación móvil. El administrador podrá visualizar en tiempo real el estado de cada galpón desde un panel web, recibir alertas automáticas ante desvíos respecto de los estándares cargados, y obtener al cierre de cada crianza un reporte con los índices calculados y el precio resultante según la tabla de doble entrada.
2.5 Soluciones similares existentes
Existen en el mercado soluciones de gestión avícola de escala industrial, como AviApp, PoultryPro o los módulos agropecuarios de ERP genéricos. Sin embargo, estas plataformas presentan las siguientes desventajas frente al desarrollo propuesto:
Están orientadas a explotaciones de mayor escala o a integradoras, con funcionalidades y costos que exceden las necesidades de un establecimiento familiar mediano.
No contemplan la lógica de negocio específica de Granja "El Moro": la tabla de doble entrada para el cálculo del precio por pollo es propia del contrato entre la granja y su empresa integradora.
No están diseñadas para el esquema de carga distribuida desde múltiples galpones por parte de distintos granjeros.
El sistema propuesto se diseñará a medida del proceso real de la granja, lo que garantiza una adopción más sencilla y una mayor adecuación a las necesidades del cliente.




2.6 Análisis FODA
El análisis FODA permite evaluar los factores internos y externos que pueden influir en el desarrollo e implementación del sistema propuesto. Esta herramienta facilita identificar las fortalezas y debilidades propias del proyecto, así como las oportunidades y amenazas presentes en su entorno de utilización.
Fortalezas
El sistema será desarrollado específicamente para las necesidades de Granja "El Moro", respetando su forma actual de trabajo y adaptando la lógica del negocio a sus procesos.
Centralizará toda la información de las crianzas en una única base de datos, mejorando la integridad, trazabilidad y disponibilidad de los datos.
La carga de información se realizará directamente desde una aplicación móvil, eliminando errores de transcripción y reduciendo los tiempos de procesamiento.
El panel web permitirá al administrador visualizar indicadores en tiempo real y recibir alertas automáticas cuando algún parámetro supere los valores establecidos.
La arquitectura basada en una API REST permitirá separar la aplicación móvil, el panel web y la base de datos, favoreciendo el mantenimiento y la incorporación de nuevas funcionalidades.
El uso de tecnologías actuales y de código abierto (FastAPI, PostgreSQL, Flutter y React) reduce costos de licencias y facilita el mantenimiento futuro del sistema.
Debilidades
La utilidad del sistema dependerá de que los granjeros registren diariamente la información de forma correcta y oportuna.
La conectividad limitada en zonas rurales puede afectar la sincronización de los datos, por lo que será necesario implementar mecanismos de funcionamiento offline.
Al tratarse de un desarrollo a medida, cualquier modificación importante en los procesos de la empresa requerirá nuevas etapas de análisis y desarrollo.
Durante la etapa inicial será necesario capacitar a los usuarios para garantizar una correcta utilización de la aplicación.
El proyecto será desarrollado por un único integrante, lo que puede incrementar los tiempos de implementación, pruebas y mantenimiento.
Oportunidades
La digitalización del proceso permitirá generar información histórica que facilite el análisis de rendimiento entre distintas crianzas y apoye la toma de decisiones.
La arquitectura del sistema permitirá incorporar en el futuro nuevos módulos, como gestión sanitaria, stock de insumos, mantenimiento de instalaciones o integración con sensores ambientales.
El desarrollo podrá adaptarse posteriormente a otros establecimientos avícolas con necesidades similares.
La disponibilidad de información en tiempo real permitirá detectar desvíos operativos con mayor rapidez, reduciendo pérdidas económicas derivadas de fallas en los galpones.
La utilización de una base de datos centralizada facilitará la generación de reportes estadísticos e indicadores para la gestión de la producción.
Amenazas
La resistencia al cambio por parte de algunos usuarios puede dificultar la adopción inicial del sistema.
Fallas en el acceso a Internet o problemas de infraestructura tecnológica pueden retrasar la sincronización de la información registrada.
Cambios en la metodología de trabajo de la empresa o en los criterios de liquidación establecidos por la empresa integradora podrían requerir modificaciones en la lógica del sistema.
La pérdida o el deterioro de los dispositivos móviles utilizados por los granjeros puede afectar temporalmente la carga de información.
La aparición de soluciones comerciales específicas para la gestión avícola podría representar una alternativa competitiva en futuras implementaciones.
Del análisis realizado se observa que las fortalezas del proyecto se encuentran principalmente en la digitalización del proceso de recolección de datos, la centralización de la información y la posibilidad de obtener indicadores en tiempo real para apoyar la toma de decisiones. Las debilidades y amenazas identificadas se relacionan principalmente con factores humanos y de infraestructura, los cuales pueden mitigarse mediante una interfaz de usuario sencilla, capacitación adecuada, mecanismos de funcionamiento sin conexión a Internet y una arquitectura flexible que facilite futuras modificaciones. En conjunto, el análisis evidencia que el proyecto resulta técnicamente sólido y presenta un potencial significativo para mejorar la gestión de las crianzas avícolas.




3. Objetivos
3.1 Objetivo general
Desarrollar un sistema informático integrado que permita la gestión digital de las crianzas avícolas de Granja "El Moro", centralizando el ingreso de datos operativos diarios, el monitoreo en tiempo real y el cálculo automatizado de los índices de rendimiento y liquidación al cierre de cada crianza.
3.2 Objetivos específicos
Desarrollar una aplicación móvil que permita a los granjeros registrar diariamente la mortandad, el consumo de agua, alimento, gas y electricidad por galpón, reemplazando el envío de datos por WhatsApp.
Desarrollar un panel web para el administrador que muestre en tiempo real el estado de cada galpón, con visualización de métricas y comparación contra estándares.
Implementar un sistema de alertas automáticas que notifique al administrador cuando algún indicador supere los umbrales definidos como normales.
Desarrollar el módulo de gestión de crianzas que incluya el alta, seguimiento y cierre de cada ciclo productivo, con cálculo automático de los índices de crecimiento (gramos/día) y conversión (kg alimento / kg peso).
Implementar la lógica de liquidación basada en la tabla de doble entrada que determina el precio por pollo faenado según los índices obtenidos al cierre de la crianza.
Mantener un historial completo de crianzas que permita realizar análisis comparativos y consultas retrospectivas.
3.3 Alcance del sistema
El sistema estará compuesto por tres componentes principales:
Aplicación móvil (Android): orientada a los granjeros para la carga diaria de datos operativos por galpón.
Panel web (administrador): orientado al propietario para el monitoreo, la gestión de crianzas y la generación de reportes.
Backend y base de datos: capa de lógica de negocio y persistencia que centraliza toda la información del sistema.
Quedan fuera del alcance de este desarrollo: la gestión de recursos humanos, la facturación hacia la empresa integradora y la integración con sistemas externos de la cadena avícola.



4. Metodología
4.1 Ciclo de vida y metodología de trabajo
Uno de los desafíos más grandes al momento de desarrollar software para usuarios con poca experiencia tecnológica es no saber de antemano cómo van a reaccionar frente a lo que uno construye. En el caso de Granja "El Moro", los granjeros llevan años trabajando con papel, planillas y mensajes de WhatsApp. Pedirles que adopten una aplicación móvil sin involucrarlos en el proceso sería un riesgo innecesario: podrían encontrarse con pantallas que no entienden, flujos que no se adaptan a su rutina diaria, o directamente con funcionalidades que no les resultan útiles.
Por ese motivo, se eligió trabajar con un modelo de desarrollo de tipo prototipo. La idea central es no esperar a tener el sistema completo para mostrárselo al usuario, sino construir versiones parciales y funcionales del sistema, presentárselas a los granjeros, escuchar su opinión y ajustar antes de seguir avanzando. Cada versión incorpora lo aprendido de la anterior, de modo que el producto va mejorando iteración a iteración hasta llegar al sistema final.
En este proyecto se trabajará con prototipos operativos, es decir, versiones que realmente funcionan: cargan datos, los almacenan y los muestran. Esto es importante porque permite que los granjeros interactúen con algo real y no con una maqueta estática, lo que hace que su feedback sea mucho más concreto y útil.
4.2 Por qué este modelo y no otro
La elección del modelo de prototipo no es casual: responde directamente a las características del proyecto y de sus usuarios. Un modelo en cascada, por ejemplo, hubiera requerido definir todos los requerimientos al inicio y no volver atrás. Eso funciona bien cuando el cliente sabe exactamente lo que quiere, pero en este caso los granjeros difícilmente puedan describir con precisión qué necesitan de una aplicación que nunca usaron. El modelo de prototipo resuelve ese problema justamente al hacer visible el sistema de forma temprana y dejar que sean los propios usuarios quienes descubran qué les falta o qué les sobra.
Como todo modelo, tiene sus limitaciones. El alcance puede crecer si no se lo controla, y la documentación tiende a quedar en segundo plano cuando el foco está puesto en desarrollar. Para mitigar esto, se definirá desde el inicio un alcance acotado para cada iteración, y se documentará formalmente lo construido antes de avanzar a la siguiente etapa.
4.3 Etapas del desarrollo
El desarrollo del sistema se organizó en siete etapas ordenadas de forma que cada una siente las bases de la siguiente. El criterio para definir este orden fue simple: no tiene sentido construir la carga de datos si primero no hay usuarios que puedan ingresar al sistema, ni tiene sentido mostrar métricas si todavía no hay datos cargados.
La primera etapa abarca la autenticación y el control de acceso. Se implementará el login, el registro de usuarios y la distinción entre los dos roles del sistema: administrador y granjero. Cada rol tendrá acceso únicamente a las funcionalidades que le corresponden.
La segunda etapa cubre la estructura central del sistema: el ABM de galpones y crianzas. El administrador podrá dar de alta una crianza, asociarle los galpones que participan en ese ciclo y asignar los granjeros responsables de cada uno. Sin esta base, no hay contexto sobre el cual registrar ni analizar nada.
La tercera etapa es el corazón operativo del sistema: la carga diaria de datos desde la aplicación móvil. Cada granjero ingresará por galpón la cantidad de muertos, el consumo de agua, alimento, gas y electricidad del día. Esta etapa reemplaza directamente el circuito actual de WhatsApp y planillas.
La cuarta etapa construye encima de la anterior: el panel web de monitoreo para el administrador. Con los datos ya cargados, el panel mostrará el estado de cada galpón en tiempo real, comparando los valores registrados contra los estándares definidos para la crianza.
La quinta etapa incorpora las alertas automáticas. Cuando algún indicador supere el umbral configurado, el sistema notificará al administrador sin que este tenga que estar revisando el panel constantemente.
La sexta etapa cubre el cierre de crianza y la liquidación. Al finalizar un ciclo productivo, el sistema calculará automáticamente los índices de crecimiento y conversión, y determinará el precio por pollo faenado consultando la tabla de doble entrada correspondiente al contrato con la empresa integradora.
La séptima y última etapa agrega el historial y los reportes. El administrador podrá consultar crianzas anteriores, comparar rendimientos entre ciclos y exportar la información que necesite.
4.4 Herramientas de desarrollo
Backend: Python con el framework FastAPI. Se selecciona por su simplicidad, rendimiento y amplia documentación. Permite construir APIs REST de manera rápida y con soporte nativo para validación de datos.
Base de datos: PostgreSQL. Base de datos relacional robusta y de código abierto, adecuada para el modelo de datos del sistema que presenta relaciones claras entre crianzas, galpones y registros diarios.
Aplicación móvil: Flutter. Framework de Google que permite generar aplicaciones nativas para Android desde una única base de código. Se selecciona por su rendimiento y porque la granja opera con dispositivos Android.
Panel web: React. Biblioteca de JavaScript ampliamente utilizada para el desarrollo de interfaces web interactivas.
Control de versiones: Git con repositorio en GitHub.
Herramienta de diseño de interfaces: Figma para el prototipado de pantallas.
Documentación de API: Swagger UI, integrado automáticamente por FastAPI.



5. Análisis de viabilidad y costos
A continuación se detalla el análisis de viabilidad del proyecto en sus dimensiones técnica, económica y legal, junto con una estimación de los costos asociados.

Dimensión
Descripción
Estado
Hardware
Computadora de desarrollo y dispositivo Android para pruebas.
Disponible
Software
Python, Flutter SDK, PostgreSQL, VS Code. Todas herramientas de código abierto o con versiones gratuitas.
Sin costo
Hosting / BD
Servidor en la nube (DigitalOcean o Railway) para el backend y la base de datos.
Aprox. USD 6/mes
Tiempo
Estimación de 20 semanas de desarrollo distribuidas entre análisis, diseño, desarrollo y pruebas.
Disponible
Legal
No se procesa información personal sensible. No existen restricciones legales para el desarrollo.
Sin inconvenientes
Económica
El desarrollo es realizado por el estudiante sin costo de mano de obra. Los costos operativos son mínimos y asumidos por la empresa cliente.
Viable


5.1 Evaluación de riesgos
Disponibilidad del cliente: los granjeros deben adoptar la aplicación móvil para que el sistema sea útil. Este riesgo se mitiga con una interfaz simple y un período de acompañamiento durante la puesta en marcha.
Conectividad en la granja: los galpones se encuentran en zona rural. Se contemplará un modo de carga offline en la aplicación móvil con sincronización posterior.
Cambios en la tabla de liquidación: el contrato con la empresa integradora puede modificar los valores de la tabla de doble entrada. El sistema permitirá actualizar estos valores sin necesidad de modificar el código.
