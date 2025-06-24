import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZendeskFormMigrator:
    def __init__(self, source_subdomain: str, source_email: str, source_token: str,
                 target_subdomain: str, target_email: str, target_token: str):
        """
        Inicializar el migrador de formularios de Zendesk
        
        Args:
            source_subdomain: Subdominio de la cuenta origen (ej: 'miempresa')
            source_email: Email del usuario en cuenta origen
            source_token: Token API de cuenta origen
            target_subdomain: Subdominio de la cuenta destino
            target_email: Email del usuario en cuenta destino  
            target_token: Token API de cuenta destino
        """
        self.source_base_url = f"https://{source_subdomain}.zendesk.com/api/v2"
        self.target_base_url = f"https://{target_subdomain}.zendesk.com/api/v2"
        
        self.source_auth = (f"{source_email}/token", source_token)
        self.target_auth = (f"{target_email}/token", target_token)
        
        # Mapeo de IDs entre cuentas
        self.field_id_mapping = {}
        self.brand_id_mapping = {}
        self.group_id_mapping = {}
        
    def _make_request(self, method: str, url: str, auth: tuple, data: dict = None) -> dict:
        """Realizar petición HTTP con manejo de errores"""
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, auth=auth, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, auth=auth, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, auth=auth, headers=headers, json=data)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición {method} {url}: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Respuesta del servidor: {e.response.text}")
            raise
    
    def get_ticket_form(self, form_id: int, from_source: bool = True) -> dict:
        """Obtener un formulario específico"""
        base_url = self.source_base_url if from_source else self.target_base_url
        auth = self.source_auth if from_source else self.target_auth
        
        url = f"{base_url}/ticket_forms/{form_id}"
        response = self._make_request('GET', url, auth)
        return response['ticket_form']
    
    def get_all_ticket_forms(self, from_source: bool = True) -> List[dict]:
        """Obtener todos los formularios"""
        base_url = self.source_base_url if from_source else self.target_base_url
        auth = self.source_auth if from_source else self.target_auth
        
        url = f"{base_url}/ticket_forms"
        response = self._make_request('GET', url, auth)
        return response['ticket_forms']
    
    def get_ticket_fields(self, from_source: bool = True) -> List[dict]:
        """Obtener todos los campos de ticket"""
        base_url = self.source_base_url if from_source else self.target_base_url
        auth = self.source_auth if from_source else self.target_auth
        
        url = f"{base_url}/ticket_fields"
        response = self._make_request('GET', url, auth)
        return response['ticket_fields']
    
    def create_ticket_field(self, field_data: dict) -> dict:
        """Crear un campo de ticket en la cuenta destino"""
        url = f"{self.target_base_url}/ticket_fields"
        
        # Limpiar datos del campo para creación
        clean_field_data = {
            'type': field_data['type'],
            'title': field_data['title'],
            'description': field_data.get('description', ''),
            'position': field_data.get('position', 0),
            'active': field_data.get('active', True),
            'required': field_data.get('required', False),
            'collapsed_for_agents': field_data.get('collapsed_for_agents', False),
            'regexp_for_validation': field_data.get('regexp_for_validation'),
            'title_in_portal': field_data.get('title_in_portal'),
            'visible_in_portal': field_data.get('visible_in_portal', True),
            'editable_in_portal': field_data.get('editable_in_portal', True),
            'required_in_portal': field_data.get('required_in_portal', False),
            'tag': field_data.get('tag'),
            'custom_field_options': field_data.get('custom_field_options', []),
            'sub_type_id': field_data.get('sub_type_id'),
            'removable': field_data.get('removable', True)
        }
        
        # Remover valores None
        clean_field_data = {k: v for k, v in clean_field_data.items() if v is not None}
        
        payload = {'ticket_field': clean_field_data}
        response = self._make_request('POST', url, self.target_auth, payload)
        return response['ticket_field']
    
    def build_field_mapping(self) -> None:
        """Construir mapeo entre campos de origen y destino"""
        logger.info("Construyendo mapeo de campos...")
        
        source_fields = self.get_ticket_fields(from_source=True)
        target_fields = self.get_ticket_fields(from_source=False)
        
        # Crear diccionario de campos destino por título
        target_fields_by_title = {field['title']: field for field in target_fields}
        
        for source_field in source_fields:
            source_id = source_field['id']
            source_title = source_field['title']
            
            # Campos estándar siempre existen con el mismo ID
            if source_field['type'] in ['subject', 'description', 'status', 'priority', 'type', 
                                      'assignee', 'group', 'requester', 'collaborator']:
                self.field_id_mapping[source_id] = source_id
                continue
            
            # Buscar campo personalizado correspondiente en destino
            if source_title in target_fields_by_title:
                target_field = target_fields_by_title[source_title]
                self.field_id_mapping[source_id] = target_field['id']
                logger.info(f"Campo mapeado: '{source_title}' {source_id} -> {target_field['id']}")
            else:
                logger.warning(f"Campo no encontrado en destino: '{source_title}' (ID: {source_id})")
    
    def migrate_missing_fields(self, form_data: dict) -> None:
        """Migrar campos faltantes del formulario"""
        logger.info("Verificando campos faltantes...")
        
        source_fields = self.get_ticket_fields(from_source=True)
        source_fields_dict = {field['id']: field for field in source_fields}
        
        missing_fields = []
        for field_id in form_data.get('ticket_field_ids', []):
            if field_id not in self.field_id_mapping:
                if field_id in source_fields_dict:
                    missing_fields.append(source_fields_dict[field_id])
        
        for field in missing_fields:
            try:
                logger.info(f"Creando campo faltante: {field['title']}")
                new_field = self.create_ticket_field(field)
                self.field_id_mapping[field['id']] = new_field['id']
                logger.info(f"Campo creado exitosamente: {field['title']} -> ID {new_field['id']}")
                time.sleep(1)  # Evitar rate limiting
            except Exception as e:
                logger.error(f"Error creando campo {field['title']}: {str(e)}")
    
    def transform_conditions(self, conditions: List[dict]) -> List[dict]:
        """Transformar condiciones del formulario para usar nuevos IDs"""
        if not conditions:
            logger.info("No hay condiciones para transformar")
            return []
            
        logger.info(f"Transformando {len(conditions)} condiciones...")
        transformed_conditions = []
        
        for i, condition in enumerate(conditions):
            logger.debug(f"Procesando condición {i+1}: {json.dumps(condition, indent=2)}")
            new_condition = {}
            
            # Copiar propiedades básicas
            for key in ['parent_field_id', 'parent_field_type', 'value', 'operator']:
                if key in condition:
                    new_condition[key] = condition[key]
            
            # Mapear parent_field_id si existe en el mapeo
            if 'parent_field_id' in condition:
                original_field_id = condition['parent_field_id']
                if original_field_id in self.field_id_mapping:
                    new_condition['parent_field_id'] = self.field_id_mapping[original_field_id]
                    logger.debug(f"Mapeado parent_field_id: {original_field_id} -> {self.field_id_mapping[original_field_id]}")
                else:
                    logger.warning(f"parent_field_id {original_field_id} no encontrado en mapeo")
                    new_condition['parent_field_id'] = original_field_id
            
            # Procesar child_fields (campos que se muestran/ocultan según la condición)
            if 'child_fields' in condition and condition['child_fields']:
                new_child_fields = []
                for child_field in condition['child_fields']:
                    new_child_field = {}
                    
                    # Copiar todas las propiedades del child_field
                    for child_key, child_value in child_field.items():
                        new_child_field[child_key] = child_value
                    
                    # Mapear el ID del campo hijo si existe
                    if 'id' in child_field:
                        original_child_id = child_field['id']
                        if original_child_id in self.field_id_mapping:
                            new_child_field['id'] = self.field_id_mapping[original_child_id]
                            logger.debug(f"Mapeado child_field id: {original_child_id} -> {self.field_id_mapping[original_child_id]}")
                        else:
                            logger.warning(f"child_field id {original_child_id} no encontrado en mapeo")
                    
                    new_child_fields.append(new_child_field)
                
                new_condition['child_fields'] = new_child_fields
                logger.debug(f"Procesados {len(new_child_fields)} child_fields")
            
            # Copiar cualquier otra propiedad que pueda existir
            for key, value in condition.items():
                if key not in ['parent_field_id', 'parent_field_type', 'value', 'operator', 'child_fields']:
                    new_condition[key] = value
            
            transformed_conditions.append(new_condition)
            logger.debug(f"Condición transformada: {json.dumps(new_condition, indent=2)}")
        
        logger.info(f"Transformación completada: {len(transformed_conditions)} condiciones procesadas")
        return transformed_conditions
    
    def create_ticket_form(self, form_data: dict, debug_mode: bool = False) -> dict:
        """Crear formulario en cuenta destino"""
        logger.info(f"Creando formulario: {form_data['name']}")
        
        # Mapear ticket_field_ids
        new_field_ids = []
        missing_fields = []
        
        for field_id in form_data.get('ticket_field_ids', []):
            if field_id in self.field_id_mapping:
                new_field_ids.append(self.field_id_mapping[field_id])
                logger.debug(f"Campo mapeado: {field_id} -> {self.field_id_mapping[field_id]}")
            else:
                logger.warning(f"Campo ID {field_id} no encontrado en mapeo")
                missing_fields.append(field_id)
        
        if missing_fields:
            logger.error(f"Campos faltantes en mapeo: {missing_fields}")
        
        # Transformar condiciones de usuario final
        end_user_conditions = form_data.get('end_user_conditions', [])
        agent_conditions = form_data.get('agent_conditions', [])
        
        logger.info(f"Condiciones end_user originales: {len(end_user_conditions)}")
        logger.info(f"Condiciones agent originales: {len(agent_conditions)}")
        
        if end_user_conditions and debug_mode:
            logger.debug(f"end_user_conditions raw: {json.dumps(end_user_conditions, indent=2)}")
        if agent_conditions and debug_mode:
            logger.debug(f"agent_conditions raw: {json.dumps(agent_conditions, indent=2)}")
        
        new_end_user_conditions = self.transform_conditions(end_user_conditions)
        new_agent_conditions = self.transform_conditions(agent_conditions)
        
        logger.info(f"Condiciones end_user transformadas: {len(new_end_user_conditions)}")
        logger.info(f"Condiciones agent transformadas: {len(new_agent_conditions)}")
        
        # Preparar datos del formulario
        new_form_data = {
            'name': form_data['name'],
            'display_name': form_data.get('display_name', form_data['name']),
            'position': form_data.get('position', 0),
            'active': form_data.get('active', True),
            'end_user_visible': form_data.get('end_user_visible', True),
            'default': form_data.get('default', False),
            'ticket_field_ids': new_field_ids,
            'in_all_brands': form_data.get('in_all_brands', True)
        }
        
        # Agregar condiciones si existen
        if new_end_user_conditions:
            new_form_data['end_user_conditions'] = new_end_user_conditions
            logger.info(f"Agregando {len(new_end_user_conditions)} condiciones end_user al formulario")
        
        if new_agent_conditions:
            new_form_data['agent_conditions'] = new_agent_conditions
            logger.info(f"Agregando {len(new_agent_conditions)} condiciones agent al formulario")
        
        if not new_end_user_conditions and not new_agent_conditions:
            logger.info("No se agregaron condiciones al formulario")
        
        # Remover valores None
        new_form_data = {k: v for k, v in new_form_data.items() if v is not None}
        
        logger.debug(f"Datos finales del formulario: {json.dumps(new_form_data, indent=2)}")
        
        url = f"{self.target_base_url}/ticket_forms"
        payload = {'ticket_form': new_form_data}
        
        try:
            response = self._make_request('POST', url, self.target_auth, payload)
            logger.info("Formulario creado exitosamente")
            return response['ticket_form']
        except Exception as e:
            logger.error(f"Error creando formulario: {str(e)}")
            # Log del payload que causó el error
            logger.error(f"Payload que causó error: {json.dumps(payload, indent=2)}")
            raise
    
    def migrate_form(self, form_id: int, debug_mode: bool = False) -> dict:
        """Migrar un formulario completo"""
        # Configurar nivel de logging según debug_mode
        if debug_mode:
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"Iniciando migración del formulario ID: {form_id}")
        
        try:
            # 1. Obtener formulario origen
            source_form = self.get_ticket_form(form_id, from_source=True)
            logger.info(f"Formulario obtenido: {source_form['name']}")
            
            # Log de información del formulario origen
            logger.info(f"Campos en formulario origen: {len(source_form.get('ticket_field_ids', []))}")
            logger.info(f"Condiciones end_user en formulario origen: {len(source_form.get('end_user_conditions', []))}")
            logger.info(f"Condiciones agent en formulario origen: {len(source_form.get('agent_conditions', []))}")
            
            if debug_mode:
                logger.debug(f"Formulario completo: {json.dumps(source_form, indent=2)}")
            
            # 2. Construir mapeo de campos
            self.build_field_mapping()
            
            # 3. Migrar campos faltantes
            self.migrate_missing_fields(source_form)
            
            # 4. Crear formulario en destino
            new_form = self.create_ticket_form(source_form, debug_mode=debug_mode)
            
            logger.info(f"Formulario migrado exitosamente: {new_form['name']} (ID: {new_form['id']})")
            
            # Verificar si las condiciones se migraron correctamente
            final_end_user_conditions = len(new_form.get('end_user_conditions', []))
            final_agent_conditions = len(new_form.get('agent_conditions', []))
            original_end_user_conditions = len(source_form.get('end_user_conditions', []))
            original_agent_conditions = len(source_form.get('agent_conditions', []))
            
            total_final = final_end_user_conditions + final_agent_conditions
            total_original = original_end_user_conditions + original_agent_conditions
            
            if total_final != total_original:
                logger.warning(f"Discrepancia en condiciones: Original={total_original}, Migrado={total_final}")
            else:
                logger.info(f"Condiciones migradas correctamente: {total_final}")
            
            return {
                'status': 'success',
                'source_form': source_form,
                'migrated_form': new_form,
                'field_mappings': self.field_id_mapping,
                'conditions_migrated': {
                    'end_user': final_end_user_conditions,
                    'agent': final_agent_conditions,
                    'total': total_final
                },
                'conditions_original': {
                    'end_user': original_end_user_conditions,
                    'agent': original_agent_conditions,
                    'total': total_original
                }
            }
            
        except Exception as e:
            logger.error(f"Error migrando formulario: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'field_mappings': self.field_id_mapping
            }
    
    def list_forms(self, from_source: bool = True) -> None:
        """Listar todos los formularios disponibles"""
        forms = self.get_all_ticket_forms(from_source)
        source_text = "origen" if from_source else "destino"
        
        print(f"\n=== Formularios en cuenta {source_text} ===")
        for form in forms:
            print(f"ID: {form['id']} | Nombre: {form['name']} | Activo: {form['active']}")

# Ejemplo de uso
def main():
    """Función principal con ejemplo de uso"""
    
    # Configuración de cuentas
    SOURCE_CONFIG = {
        'subdomain': 'con-zerviz-cx',
        'email': 'pablo.zarricueta@zervizgroup.com',
        'token': 'tZIe9WBZZTnVBn6Y8WWqL12T1CPxQmMmIGmINakl'
    }
    
    TARGET_CONFIG = {
        'subdomain': 'd3v-testpostmaster', 
        'email': 'juan.gonzalez@zerviz.cl',
        'token': 'Tx92fg798Wu3ODs3A4WYC5p4dNjCN5ZaaWSDfzor'
    }
    # Crear instancia del migrador
    migrator = ZendeskFormMigrator(
        SOURCE_CONFIG['subdomain'], SOURCE_CONFIG['email'], SOURCE_CONFIG['token'],
        TARGET_CONFIG['subdomain'], TARGET_CONFIG['email'], TARGET_CONFIG['token']
    )
    
    # Listar formularios disponibles
    print("Obteniendo lista de formularios...")
    migrator.list_forms(from_source=True)
    
    # Migrar formulario específico
    form_id_to_migrate = input("\nIngresa el ID del formulario a migrar: ")
    
    try:
        form_id = int(form_id_to_migrate)
        
        # Preguntar si quiere modo debug
        debug_input = input("¿Activar modo debug para ver detalles? (s/n): ").lower().strip()
        debug_mode = debug_input in ['s', 'si', 'sí', 'y', 'yes']
        
        result = migrator.migrate_form(form_id, debug_mode=debug_mode)
        
        if result['status'] == 'success':
            print(f"\n✅ Migración exitosa!")
            print(f"Formulario creado con ID: {result['migrated_form']['id']}")
            print(f"Mapeo de campos utilizado: {len(result['field_mappings'])} campos mapeados")
            
            conditions_orig = result['conditions_original']
            conditions_migr = result['conditions_migrated']
            
            print(f"\nCondiciones originales:")
            print(f"  - End user: {conditions_orig['end_user']}")
            print(f"  - Agent: {conditions_orig['agent']}")
            print(f"  - Total: {conditions_orig['total']}")
            
            print(f"\nCondiciones migradas:")
            print(f"  - End user: {conditions_migr['end_user']}")
            print(f"  - Agent: {conditions_migr['agent']}")
            print(f"  - Total: {conditions_migr['total']}")
            
            if conditions_orig['total'] > 0 and conditions_migr['total'] == 0:
                print("\n⚠️  ADVERTENCIA: El formulario original tenía condiciones pero no se migraron.")
                print("Revisa los logs para más detalles.")
            elif conditions_orig['total'] != conditions_migr['total']:
                print(f"\n⚠️  ADVERTENCIA: Discrepancia en número de condiciones.")
                print("Revisa los logs para más detalles.")
        else:
            print(f"\n❌ Error en migración: {result['error']}")
            
    except ValueError:
        print("Por favor ingresa un ID válido (número)")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()