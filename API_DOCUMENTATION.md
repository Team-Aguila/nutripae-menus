# API de Cobertura del PAE - Documentación de Endpoints

## Información General
- **Base URL**: `http://127.0.0.1:8000`
- **Versión**: v1
- **Prefijo de API**: `/api/v1`

---

## 1. Departments (Departamentos)

### 1.1 Listar Departamentos

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/departments/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 100)

**200 Response body**
```json
[
  {
    "id": 1,
    "dane_code": "01",
    "name": "Antioquia",
    "created_at": "2025-07-05T14:22:55.946841",
    "updated_at": "2025-07-05T14:22:55.948771",
    "number_of_towns": 5
  },
  {
    "id": 4,
    "dane_code": "04",
    "name": "Atlántico",
    "created_at": "2025-07-05T14:22:56.446954",
    "updated_at": "2025-07-05T14:22:56.448212",
    "number_of_towns": 5
  }
]
```

### 1.2 Obtener Departamento por ID

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/departments/1
```

**200 Response body**
```json
{
  "id": 1,
  "dane_code": "01",
  "name": "Antioquia",
  "created_at": "2025-07-05T14:22:55.946841",
  "updated_at": "2025-07-05T14:22:55.948771",
  "deleted_at": null,
  "number_of_towns": 5
}
```

### 1.3 Crear Departamento

**Request URL**
```
POST http://127.0.0.1:8000/api/v1/departments/
```

**Request body**
```json
{
  "dane_code": "99",
  "name": "Test Department"
}
```

**200 Response body**
```json
{
  "id": 11,
  "dane_code": "99",
  "name": "Test Department",
  "created_at": "2025-07-05T14:40:55.607056",
  "updated_at": "2025-07-05T14:40:55.607081",
  "deleted_at": null,
  "number_of_towns": 0
}
```

---

## 2. Towns (Municipios)

### 2.1 Listar Municipios

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/towns/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 100)

**200 Response body**
```json
[
  {
    "name": "Arjona",
    "dane_code": "06030",
    "department_id": 6,
    "id": 30,
    "created_at": "2025-07-05T14:22:57.012199",
    "updated_at": "2025-07-05T14:22:57.013377",
    "number_of_institutions": 1
  },
  {
    "name": "Barrancabermeja",
    "dane_code": "05025",
    "department_id": 5,
    "id": 25,
    "created_at": "2025-07-05T14:22:56.784562",
    "updated_at": "2025-07-05T14:22:56.788620",
    "number_of_institutions": 0
  }
]
```

### 2.2 Crear Municipio

**Request URL**
```
POST http://127.0.0.1:8000/api/v1/towns/
```

**Request body**
```json
{
  "name": "Nuevo Municipio",
  "dane_code": "99001",
  "department_id": 1
}
```

---

## 3. Institutions (Instituciones)

### 3.1 Listar Instituciones

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/institutions/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 100)

**200 Response body**
```json
[
  {
    "name": "Acosta, Herrera and Ospino",
    "dane_code": "01003014",
    "town_id": 3,
    "id": 14,
    "created_at": "2025-07-05T14:23:00.432631",
    "updated_at": "2025-07-05T14:23:00.433224",
    "number_of_campuses": 1
  },
  {
    "name": "Aguirre LLC",
    "dane_code": "03014013",
    "town_id": 14,
    "id": 13,
    "created_at": "2025-07-05T14:23:00.408380",
    "updated_at": "2025-07-05T14:23:00.410111",
    "number_of_campuses": 0
  }
]
```

### 3.2 Obtener Institución por ID

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/institutions/14
```

**200 Response body**
```json
{
  "name": "Acosta, Herrera and Ospino",
  "dane_code": "01003014",
  "town_id": 3,
  "id": 14,
  "created_at": "2025-07-05T14:23:00.432631",
  "updated_at": "2025-07-05T14:23:00.433224",
  "number_of_campuses": 1
}
```

### 3.3 Crear Institución

**Request URL**
```
POST http://127.0.0.1:8000/api/v1/institutions/
```

**Request body**
```json
{
  "name": "Nueva Institución",
  "dane_code": "99001001",
  "town_id": 1
}
```

---

## 4. Campuses (Sedes)

### 4.1 Listar Sedes

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/campuses/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 100)

**200 Response body**
```json
[
  {
    "name": "Sede Benavides",
    "dane_code": "06027006024",
    "institution_id": 6,
    "address": "Carrera 8ª # 58-78 Sur\nCasa 6\n914330\nTarapacá, Amazonas",
    "latitude": 50.1039535,
    "longitude": -174.846304,
    "id": 24,
    "created_at": "2025-07-05T14:23:01.686631",
    "updated_at": "2025-07-05T14:23:01.687168",
    "number_of_coverages": 27
  },
  {
    "name": "Sede Burbano",
    "dane_code": "03014009011",
    "institution_id": 9,
    "address": "Calle 4ª # 81-97 Sur\nOficina 55\n153530\nMaripí, Boyacá",
    "latitude": -13.9608235,
    "longitude": 133.998549,
    "id": 11,
    "created_at": "2025-07-05T14:23:01.351245",
    "updated_at": "2025-07-05T14:23:01.351771",
    "number_of_coverages": 31
  }
]
```

### 4.2 Crear Sede

**Request URL**
```
POST http://127.0.0.1:8000/api/v1/campuses/
```

**Request body**
```json
{
  "name": "Nueva Sede",
  "dane_code": "99001001001",
  "institution_id": 1,
  "address": "Dirección de la nueva sede",
  "latitude": 4.6097,
  "longitude": -74.0817
}
```

---

## 5. Beneficiaries (Beneficiarios)

### 5.1 Listar Beneficiarios

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/beneficiaries/?skip=0&limit=10000
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 10000, máximo: 10000)

**200 Response body**
```json
[
  {
    "document_type_id": 2,
    "number_document": "857-82-9378",
    "first_name": "Martha",
    "second_name": "Viviana",
    "first_surname": "Gaviria",
    "second_surname": "Restrepo",
    "birth_date": "2015-04-22",
    "gender_id": 2,
    "grade_id": 10,
    "etnic_group_id": null,
    "victim_conflict": false,
    "disability_type_id": 1,
    "attendant_number": 1,
    "attendant_name": null,
    "attendant_phone": null,
    "attendant_relationship": null,
    "retirement_date": null,
    "retirement_reason": null,
    "id": "ac82bea4-cfcb-40a9-883d-ceb6ef7394ab",
    "created_at": "2025-07-05T14:23:02.657187",
    "updated_at": "2025-07-05T14:23:02.657794",
    "deleted_at": null
  }
]
```

### 5.2 Obtener Beneficiario por ID (Con Detalles)

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/beneficiaries/ac82bea4-cfcb-40a9-883d-ceb6ef7394ab
```

**200 Response body**
```json
{
  "document_type_id": 2,
  "number_document": "857-82-9378",
  "first_name": "Martha",
  "second_name": "Viviana",
  "first_surname": "Gaviria",
  "second_surname": "Restrepo",
  "birth_date": "2015-04-22",
  "gender_id": 2,
  "grade_id": 10,
  "etnic_group_id": null,
  "victim_conflict": false,
  "disability_type_id": 1,
  "attendant_number": 1,
  "attendant_name": null,
  "attendant_phone": null,
  "attendant_relationship": null,
  "retirement_date": null,
  "retirement_reason": null,
  "id": "ac82bea4-cfcb-40a9-883d-ceb6ef7394ab",
  "created_at": "2025-07-05T14:23:02.657187",
  "updated_at": "2025-07-05T14:23:02.657794",
  "deleted_at": null,
  "document_type": {
    "id": 2,
    "name": "documento de identidad"
  },
  "gender": {
    "name": "femenino",
    "id": 2
  },
  "grade": {
    "id": 10,
    "name": "cuarto"
  },
  "etnic_group": null,
  "disability_type": {
    "id": 1,
    "name": "visual"
  },
  "coverage": [
    {
      "id": "530af7a6-a7ce-4144-a4de-b5c7a70729f7",
      "updated_at": "2025-07-05T14:23:29.256762",
      "benefit_type_id": 1,
      "beneficiary_id": "ac82bea4-cfcb-40a9-883d-ceb6ef7394ab",
      "active": true,
      "created_at": "2025-07-05T14:23:29.256069",
      "deleted_at": null,
      "campus_id": 23
    }
  ]
}
```

### 5.3 Crear Beneficiario

**Request URL**
```
POST http://127.0.0.1:8000/api/v1/beneficiaries/
```

**Request body**
```json
{
  "document_type_id": 1,
  "number_document": "123456789",
  "first_name": "Juan",
  "second_name": "Carlos",
  "first_surname": "Pérez",
  "second_surname": "González",
  "birth_date": "2010-05-15",
  "gender_id": 1,
  "grade_id": 7,
  "etnic_group_id": 1,
  "victim_conflict": false,
  "disability_type_id": null,
  "attendant_number": 1,
  "attendant_name": "María González",
  "attendant_phone": "3001234567",
  "attendant_relationship": "Madre"
}
```

---

## 6. Coverages (Coberturas)

### 6.1 Listar Coberturas

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/coverages/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 100)

**200 Response body**
```json
[
  {
    "active": true,
    "benefit_type_id": 1,
    "campus_id": 23,
    "beneficiary_id": "ac82bea4-cfcb-40a9-883d-ceb6ef7394ab",
    "id": "530af7a6-a7ce-4144-a4de-b5c7a70729f7",
    "created_at": "2025-07-05T14:23:29.256069",
    "updated_at": "2025-07-05T14:23:29.256762",
    "deleted_at": null
  },
  {
    "active": true,
    "benefit_type_id": 2,
    "campus_id": 17,
    "beneficiary_id": "56fd3d4d-e068-4348-9acf-9d34f052ceb9",
    "id": "6fbe8a42-ce90-463f-8140-82474be44487",
    "created_at": "2025-07-05T14:23:29.286897",
    "updated_at": "2025-07-05T14:23:29.287472",
    "deleted_at": null
  }
]
```

### 6.2 Crear Cobertura

**Request URL**
```
POST http://127.0.0.1:8000/api/v1/coverages/
```

**Request body**
```json
{
  "active": true,
  "benefit_type_id": 1,
  "campus_id": 1,
  "beneficiary_id": "ac82bea4-cfcb-40a9-883d-ceb6ef7394ab"
}
```

---

## 7. Parametrics (Datos Paramétricos)

### 7.1 Tipos de Beneficio

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/parametrics/benefit-types
```

**200 Response body**
```json
[
  {
    "name": "desayuno",
    "id": 1
  },
  {
    "name": "almuerzo",
    "id": 2
  },
  {
    "name": "refrigerio",
    "id": 3
  }
]
```

### 7.2 Grados Académicos

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/parametrics/grades
```

**200 Response body**
```json
[
  {
    "id": 1,
    "name": "inicial 0-1 años"
  },
  {
    "id": 2,
    "name": "inicial 1-2 años"
  },
  {
    "id": 3,
    "name": "inicial 2-3 años"
  },
  {
    "id": 4,
    "name": "pre-jardín"
  },
  {
    "id": 5,
    "name": "jardín"
  },
  {
    "id": 6,
    "name": "transición"
  },
  {
    "id": 7,
    "name": "primero"
  },
  {
    "id": 8,
    "name": "segundo"
  },
  {
    "id": 9,
    "name": "tercero"
  },
  {
    "id": 10,
    "name": "cuarto"
  },
  {
    "id": 11,
    "name": "quinto"
  },
  {
    "id": 12,
    "name": "sexto"
  },
  {
    "id": 13,
    "name": "séptimo"
  },
  {
    "id": 14,
    "name": "octavo"
  },
  {
    "id": 15,
    "name": "noveno"
  },
  {
    "id": 16,
    "name": "décimo"
  },
  {
    "id": 17,
    "name": "once"
  }
]
```

### 7.3 Géneros

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/parametrics/genders
```

**200 Response body**
```json
[
  {
    "name": "masculino",
    "id": 1
  },
  {
    "name": "femenino",
    "id": 2
  },
  {
    "name": "otro",
    "id": 3
  }
]
```

### 7.4 Tipos de Documento

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/parametrics/document-types
```

**200 Response body**
```json
[
  {
    "id": 1,
    "name": "registro de nacimiento"
  },
  {
    "id": 2,
    "name": "documento de identidad"
  },
  {
    "id": 3,
    "name": "pasaporte"
  },
  {
    "id": 4,
    "name": "documento extranjero"
  }
]
```

### 7.5 Tipos de Discapacidad

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/parametrics/disability-types
```

**200 Response body**
```json
[
  {
    "id": 1,
    "name": "visual"
  },
  {
    "id": 2,
    "name": "auditiva"
  },
  {
    "id": 3,
    "name": "motora"
  },
  {
    "id": 4,
    "name": "intelectual"
  },
  {
    "id": 5,
    "name": "multiple"
  }
]
```

### 7.6 Grupos Étnicos

**Request URL**
```
GET http://127.0.0.1:8000/api/v1/parametrics/etnic-groups
```

**200 Response body**
```json
[
  {
    "id": 1,
    "name": "afro"
  },
  {
    "id": 2,
    "name": "indígena"
  },
  {
    "id": 3,
    "name": "palenquero"
  },
  {
    "id": 4,
    "name": "rom"
  },
  {
    "id": 5,
    "name": "mestizo"
  },
  {
    "id": 6,
    "name": "otro"
  }
]
```

---

## 8. Root Endpoint

### 8.1 Endpoint Raíz

**Request URL**
```
GET http://127.0.0.1:8000/
```

**200 Response body**
```json
{
  "message": "Welcome to the PAE Coverage API"
}
```

---

## Códigos de Estado HTTP

- **200 OK**: Solicitud exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Datos de entrada inválidos
- **404 Not Found**: Recurso no encontrado
- **422 Unprocessable Entity**: Error de validación de datos
- **500 Internal Server Error**: Error interno del servidor

## Notas Importantes

1. **IDs de Beneficiarios y Coberturas**: Utilizan UUID formato string
2. **IDs de otras entidades**: Utilizan enteros secuenciales
3. **Fechas**: Formato ISO 8601 (YYYY-MM-DDTHH:MM:SS.ssssss)
4. **Fechas de nacimiento**: Formato YYYY-MM-DD
5. **Paginación**: Todos los endpoints de listado soportan parámetros `skip` y `limit`
6. **Campos opcionales**: Los campos marcados como `null` son opcionales en las solicitudes POST
7. **Eliminación suave**: Los registros tienen un campo `deleted_at` para eliminación suave

## Autenticación

Actualmente la API no requiere autenticación, pero se recomienda implementar autenticación para uso en producción.

## CORS

La API permite solicitudes desde cualquier origen. Para producción, se recomienda configurar orígenes específicos. 