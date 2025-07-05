# API de Menús del PAE - Documentación de Endpoints GET

## Información General
- **Base URL**: `http://127.0.0.1:8001`
- **Versión**: v1
- **Prefijo de API**: `/api/v1`

---

## 1. Ingredients (Ingredientes)

### 1.1 Listar Todos los Ingredientes

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/ingredients/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 1000)
- `status` (opcional): Filtrar por estado del ingrediente (active/inactive)
- `category` (opcional): Filtrar por categoría del ingrediente
- `search` (opcional): Término de búsqueda para el nombre del ingrediente

**200 Response body**
```json
[
  {
    "name": "Arroz",
    "base_unit_of_measure": "kg",
    "status": "active",
    "description": "Arroz blanco para preparaciones principales",
    "category": "cereales",
    "_id": "68698c96592f38947ff0a6eb",
    "created_at": "2025-07-05T20:35:34.936000",
    "updated_at": "2025-07-05T20:35:34.936000"
  },
  {
    "name": "Pollo",
    "base_unit_of_measure": "kg",
    "status": "active",
    "description": "Pollo fresco para preparaciones",
    "category": "proteinas",
    "_id": "68698cb8592f38947ff0a6ec",
    "created_at": "2025-07-05T20:36:08.532000",
    "updated_at": "2025-07-05T20:36:08.532000"
  }
]
```

### 1.2 Listar Ingredientes Activos

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/ingredients/active?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 1000)
- `category` (opcional): Filtrar por categoría del ingrediente
- `search` (opcional): Término de búsqueda para el nombre del ingrediente

**200 Response body**
```json
[
  {
    "name": "Arroz",
    "base_unit_of_measure": "kg",
    "status": "active",
    "description": "Arroz blanco para preparaciones principales",
    "category": "cereales",
    "_id": "68698c96592f38947ff0a6eb",
    "created_at": "2025-07-05T20:35:34.936000",
    "updated_at": "2025-07-05T20:35:34.936000"
  }
]
```

### 1.3 Listar Ingredientes Detallados

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/ingredients/detailed?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 1000)
- `status` (opcional): Filtrar por estado del ingrediente (active/inactive)
- `category` (opcional): Filtrar por categoría del ingrediente
- `search` (opcional): Término de búsqueda para el nombre del ingrediente

**200 Response body**
```json
[
  {
    "name": "Arroz",
    "base_unit_of_measure": "kg",
    "status": "active",
    "description": "Arroz blanco para preparaciones principales",
    "category": "cereales",
    "_id": "68698c96592f38947ff0a6eb",
    "created_at": "2025-07-05T20:35:34.936000",
    "updated_at": "2025-07-05T20:35:34.936000",
    "menu_usage": {
      "dish_count": 1,
      "menu_cycle_count": 2,
      "dish_names": [
        "Arroz con Pollo"
      ],
      "last_used_date": "2025-07-05T20:45:01.916000"
    }
  }
]
```

### 1.4 Obtener Estadísticas de Ingredientes

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/ingredients/statistics
```

**200 Response body**
```json
{
  "total_ingredients": 17,
  "active_ingredients": 17,
  "inactive_ingredients": 0,
  "categories_count": 8,
  "categories": [
    "cereales",
    "proteinas",
    "legumbres",
    "verduras",
    "aceites",
    "condimentos",
    "tuberculos",
    "lacteos",
    "frutas"
  ]
}
```

### 1.5 Obtener Ingrediente por ID

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/ingredients/{ingredient_id}
```

**200 Response body**
```json
{
  "name": "Arroz",
  "base_unit_of_measure": "kg",
  "status": "active",
  "description": "Arroz blanco para preparaciones principales",
  "category": "cereales",
  "_id": "68698c96592f38947ff0a6eb",
  "created_at": "2025-07-05T20:35:34.936000",
  "updated_at": "2025-07-05T20:35:34.936000"
}
```

### 1.6 Obtener Ingrediente Detallado por ID

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/ingredients/{ingredient_id}/detailed
```

**200 Response body**
```json
{
  "name": "Arroz",
  "base_unit_of_measure": "kg",
  "status": "active",
  "description": "Arroz blanco para preparaciones principales",
  "category": "cereales",
  "_id": "68698c96592f38947ff0a6eb",
  "created_at": "2025-07-05T20:35:34.936000",
  "updated_at": "2025-07-05T20:35:34.936000",
  "menu_usage": {
    "dish_count": 1,
    "menu_cycle_count": 2,
    "dish_names": [
      "Arroz con Pollo"
    ],
    "last_used_date": "2025-07-05T20:45:01.916000"
  }
}
```

---

## 2. Dishes (Platos)

### 2.1 Listar Todos los Platos

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/dishes/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 1000)
- `name` (opcional): Filtrar por nombre del plato
- `status` (opcional): Filtrar por estado del plato (active/inactive)
- `meal_type` (opcional): Filtrar por tipo de comida (desayuno/almuerzo/refrigerio)

**200 Response body**
```json
[
  {
    "name": "Arroz con Pollo",
    "description": "Arroz con pollo tradicional",
    "status": "active",
    "compatible_meal_types": [
      "almuerzo"
    ],
    "recipe": {
      "ingredients": [
        {
          "ingredient_id": "68698c96592f38947ff0a6eb",
          "quantity": 0.5,
          "unit": "kg"
        },
        {
          "ingredient_id": "68698cb8592f38947ff0a6ec",
          "quantity": 0.3,
          "unit": "kg"
        }
      ]
    },
    "nutritional_info": {
      "calories": 350.0,
      "protein": 25.0,
      "carbohydrates": 45.0,
      "fat": 8.0,
      "fiber": null,
      "sodium": null,
      "calcium": null,
      "iron": null,
      "vitamin_c": null,
      "vitamin_a": null,
      "photo_url": null
    },
    "dish_type": "protein",
    "_id": "68698d1f592f38947ff0a6f7",
    "created_at": "2025-07-05T20:37:51.444000",
    "updated_at": "2025-07-05T20:37:51.444000",
    "associated_menus": []
  }
]
```

### 2.2 Obtener Plato por ID

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/dishes/{dish_id}
```

**200 Response body**
```json
{
  "name": "Arroz con Pollo",
  "description": "Arroz con pollo tradicional",
  "status": "active",
  "compatible_meal_types": [
    "almuerzo"
  ],
  "recipe": {
    "ingredients": [
      {
        "ingredient_id": "68698c96592f38947ff0a6eb",
        "quantity": 0.5,
        "unit": "kg"
      },
      {
        "ingredient_id": "68698cb8592f38947ff0a6ec",
        "quantity": 0.3,
        "unit": "kg"
      }
    ]
  },
  "nutritional_info": {
    "calories": 350.0,
    "protein": 25.0,
    "carbohydrates": 45.0,
    "fat": 8.0,
    "fiber": null,
    "sodium": null,
    "calcium": null,
    "iron": null,
    "vitamin_c": null,
    "vitamin_a": null,
    "photo_url": null
  },
  "dish_type": "protein",
  "_id": "68698d1f592f38947ff0a6f7",
  "created_at": "2025-07-05T20:37:51.444000",
  "updated_at": "2025-07-05T20:37:51.444000",
  "associated_menus": []
}
```

---

## 3. Menu Cycles (Ciclos de Menú)

### 3.1 Listar Todos los Ciclos de Menú

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/menu-cycles/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 1000)
- `name` (opcional): Filtrar por nombre del ciclo de menú
- `status` (opcional): Filtrar por estado del ciclo (active/inactive)
- `duration_days` (opcional): Filtrar por duración en días

**200 Response body**
```json
[
  {
    "name": "Ciclo Básico Semanal",
    "description": "Ciclo básico de 3 días con desayuno, almuerzo y refrigerio",
    "status": "active",
    "duration_days": 3,
    "daily_menus": [
      {
        "day": 1,
        "breakfast_dish_ids": [
          "68698d35592f38947ff0a6f8"
        ],
        "lunch_dish_ids": [
          "68698d1f592f38947ff0a6f7",
          "68698d43592f38947ff0a6fa"
        ],
        "snack_dish_ids": [
          "68698d53592f38947ff0a6fb"
        ]
      }
    ],
    "_id": "68698d6a592f38947ff0a6fc",
    "created_at": "2025-07-05T20:39:06.504000",
    "updated_at": "2025-07-05T20:39:06.504000"
  }
]
```

### 3.2 Obtener Ciclo de Menú por ID

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/menu-cycles/{menu_cycle_id}
```

**200 Response body**
```json
{
  "name": "Ciclo Básico Semanal",
  "description": "Ciclo básico de 3 días con desayuno, almuerzo y refrigerio",
  "status": "active",
  "duration_days": 3,
  "daily_menus": [
    {
      "day": 1,
      "breakfast_dish_ids": [
        "68698d35592f38947ff0a6f8"
      ],
      "lunch_dish_ids": [
        "68698d1f592f38947ff0a6f7",
        "68698d43592f38947ff0a6fa"
      ],
      "snack_dish_ids": [
        "68698d53592f38947ff0a6fb"
      ]
    },
    {
      "day": 2,
      "breakfast_dish_ids": [
        "68698d35592f38947ff0a6f8"
      ],
      "lunch_dish_ids": [
        "68698d40592f38947ff0a6f9",
        "68698d43592f38947ff0a6fa"
      ],
      "snack_dish_ids": [
        "68698d53592f38947ff0a6fb"
      ]
    },
    {
      "day": 3,
      "breakfast_dish_ids": [
        "68698d35592f38947ff0a6f8"
      ],
      "lunch_dish_ids": [
        "68698d1f592f38947ff0a6f7",
        "68698d40592f38947ff0a6f9"
      ],
      "snack_dish_ids": [
        "68698d53592f38947ff0a6fb"
      ]
    }
  ],
  "_id": "68698d6a592f38947ff0a6fc",
  "created_at": "2025-07-05T20:39:06.504000",
  "updated_at": "2025-07-05T20:39:06.504000"
}
```

---

## 4. Menu Schedules (Horarios de Menú)

### 4.1 Listar Todos los Horarios de Menú

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/menu-schedules/?skip=0&limit=100
```

**Parámetros Query**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100, máximo: 1000)
- `status` (opcional): Filtrar por estado del horario (active/future/completed/cancelled)
- `menu_cycle_id` (opcional): Filtrar por ID del ciclo de menú
- `location_id` (opcional): Filtrar por ID de ubicación (campus o municipio)
- `location_type` (opcional): Filtrar por tipo de ubicación (campus/town)
- `start_date_from` (opcional): Filtrar horarios que empiecen desde esta fecha
- `start_date_to` (opcional): Filtrar horarios que empiecen hasta esta fecha
- `end_date_from` (opcional): Filtrar horarios que terminen desde esta fecha
- `end_date_to` (opcional): Filtrar horarios que terminen hasta esta fecha

**200 Response body**
```json
[
  {
    "menu_cycle_id": "68698d6a592f38947ff0a6fc",
    "coverage": [
      {
        "location_id": "24",
        "location_type": "campus",
        "location_name": "Sede Benavides"
      },
      {
        "location_id": "11",
        "location_type": "campus",
        "location_name": "Sede Burbano"
      },
      {
        "location_id": "30",
        "location_type": "town",
        "location_name": "Arjona"
      }
    ],
    "start_date": "2025-07-07",
    "end_date": "2025-07-15",
    "status": "future",
    "cancellation_info": null,
    "_id": "68698dd6592f38947ff0a6fd",
    "created_at": "2025-07-05T20:39:50.845000",
    "updated_at": "2025-07-05T20:39:50.845000"
  }
]
```

### 4.2 Obtener Horario de Menú por ID

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/menu-schedules/{schedule_id}
```

**200 Response body**
```json
{
  "menu_cycle_id": "68698d6a592f38947ff0a6fc",
  "coverage": [
    {
      "location_id": "24",
      "location_type": "campus",
      "location_name": "Sede Benavides"
    },
    {
      "location_id": "11",
      "location_type": "campus",
      "location_name": "Sede Burbano"
    },
    {
      "location_id": "30",
      "location_type": "town",
      "location_name": "Arjona"
    }
  ],
  "start_date": "2025-07-07",
  "end_date": "2025-07-15",
  "status": "future",
  "cancellation_info": null,
  "_id": "68698dd6592f38947ff0a6fd",
  "created_at": "2025-07-05T20:39:50.845000",
  "updated_at": "2025-07-05T20:39:50.845000"
}
```

### 4.3 Obtener Vista Detallada del Horario

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/menu-schedules/{schedule_id}/detailed
```

**200 Response body**
```json
{
  "id": "68698dd6592f38947ff0a6fd",
  "menu_cycle_id": "68698d6a592f38947ff0a6fc",
  "menu_cycle_name": "Ciclo Básico Semanal",
  "coverage": [
    {
      "location_id": "24",
      "location_type": "campus",
      "location_name": "Sede Benavides"
    }
  ],
  "start_date": "2025-07-07",
  "end_date": "2025-07-15",
  "status": "future",
  "cancellation_info": null,
  "created_at": "2025-07-05T20:39:50.845000",
  "updated_at": "2025-07-05T20:39:50.845000",
  "daily_menus": [
    {
      "location_id": "24",
      "location_name": "Sede Benavides",
      "location_type": "campus",
      "menu_date": "2025-07-07",
      "cycle_day": 1,
      "breakfast": [
        {
          "id": "68698d35592f38947ff0a6f8",
          "name": "Huevos Revueltos",
          "description": "Huevos revueltos con cebolla",
          "nutritional_info": {
            "calories": 180,
            "protein": 12,
            "photo_url": null
          }
        }
      ],
      "lunch": [
        {
          "id": "68698d1f592f38947ff0a6f7",
          "name": "Arroz con Pollo",
          "description": "Arroz con pollo tradicional",
          "nutritional_info": {
            "calories": 350,
            "protein": 25,
            "photo_url": null
          }
        }
      ],
      "snack": [
        {
          "id": "68698d53592f38947ff0a6fb",
          "name": "Huevo Cocido",
          "description": "Huevo cocido simple",
          "nutritional_info": {
            "calories": 140,
            "protein": 12,
            "photo_url": null
          }
        }
      ]
    }
  ],
  "total_days": 9,
  "total_locations": 3
}
```

### 4.4 Obtener Menú Efectivo para Ciudadanos

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/menu-schedules/citizen-menu/{location_id}?location_type=campus&query_date=2025-07-07
```

**Parámetros Query**
- `location_type` (requerido): Tipo de ubicación (campus/town)
- `query_date` (requerido): Fecha para consultar el menú (formato YYYY-MM-DD)

**200 Response body**
```json
{
  "location_id": "24",
  "location_name": "Sede Benavides",
  "location_type": "campus",
  "menu_date": "2025-07-07",
  "menu_cycle_name": "Ciclo Básico Semanal",
  "breakfast": [
    {
      "id": "68698d35592f38947ff0a6f8",
      "name": "Huevos Revueltos",
      "description": "Huevos revueltos con cebolla",
      "nutritional_info": {
        "calories": 180,
        "protein": 12,
        "photo_url": null
      }
    }
  ],
  "lunch": [
    {
      "id": "68698d1f592f38947ff0a6f7",
      "name": "Arroz con Pollo",
      "description": "Arroz con pollo tradicional",
      "nutritional_info": {
        "calories": 350,
        "protein": 25,
        "photo_url": null
      }
    }
  ],
  "snack": [
    {
      "id": "68698d53592f38947ff0a6fb",
      "name": "Huevo Cocido",
      "description": "Huevo cocido simple",
      "nutritional_info": {
        "calories": 140,
        "protein": 12,
        "photo_url": null
      }
    }
  ],
  "is_available": true,
  "message": null
}
```

---

## 5. Nutritional Analysis (Análisis Nutricional)

### 5.1 Generar Reporte Nutricional Completo

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/nutritional-analysis/report/{schedule_id}
```

**Descripción**
Genera un reporte completo de análisis nutricional para un horario de menú específico. Incluye análisis diario de grupos de alimentos y nutrientes, promedios diarios, puntaje de adecuación nutricional y recomendaciones.

**200 Response body**
```json
{
  "menu_schedule_id": "68698ef4592f38947ff0a708",
  "menu_cycle_name": "Ciclo Básico Semanal",
  "analysis_period": {
    "start_date": "2025-08-06",
    "end_date": "2025-08-12"
  },
  "location_count": 2,
  "total_days": 7,
  "daily_analysis": [
    {
      "date": "2025-08-06",
      "cycle_day": 1,
      "food_groups": [
        {
          "food_group": "protein",
          "total_portions": 3.0,
          "dishes_count": 3,
          "main_dishes": ["Arroz con Pollo", "Huevos Revueltos", "Huevo Cocido"]
        },
        {
          "food_group": "grains",
          "total_portions": 1.0,
          "dishes_count": 1,
          "main_dishes": ["Papas Cocidas"]
        }
      ],
      "nutrients": {
        "total_calories": 820.0,
        "total_protein": 52.0,
        "total_carbohydrates": 83.0,
        "total_fat": 32.0,
        "total_fiber": 0.0,
        "total_calcium": 0.0,
        "total_iron": 0.0,
        "total_vitamin_c": 0.0,
        "total_vitamin_a": 0.0
      },
      "total_dishes": 4
    }
  ],
  "average_daily_nutrients": {
    "total_calories": 837.14,
    "total_protein": 54.29,
    "total_carbohydrates": 85.86,
    "total_fat": 30.86,
    "total_fiber": 0.0,
    "total_calcium": 0.0,
    "total_iron": 0.0,
    "total_vitamin_c": 0.0,
    "total_vitamin_a": 0.0
  },
  "average_daily_food_groups": [
    {
      "food_group": "protein",
      "total_portions": 3.29,
      "dishes_count": 3,
      "main_dishes": ["Arroz con Pollo", "Huevo Cocido", "Huevos Revueltos", "Frijoles Guisados"]
    },
    {
      "food_group": "grains",
      "total_portions": 0.71,
      "dishes_count": 0,
      "main_dishes": ["Papas Cocidas"]
    }
  ],
  "nutritional_adequacy_score": 35.0,
  "recommendations": [
    "Consider increasing portion sizes or adding more calorie-dense foods to meet energy needs",
    "Add more dairy products or calcium-rich foods like cheese, yogurt, or fortified foods",
    "Include iron-rich foods such as red meat, beans, or fortified cereals",
    "Add fresh fruits to provide vitamins, minerals, and fiber",
    "Include more vegetables for essential vitamins and minerals",
    "Increase food group diversity to ensure balanced nutrition"
  ]
}
```

### 5.2 Obtener Análisis de Grupos de Alimentos

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/nutritional-analysis/food-groups/{schedule_id}
```

**Descripción**
Obtiene un análisis detallado de la distribución de grupos de alimentos para un horario de menú específico.

**200 Response body**
```json
{
  "menu_schedule_id": "68698ef4592f38947ff0a708",
  "menu_cycle_name": "Ciclo Básico Semanal",
  "analysis_period": {
    "start_date": "2025-08-06",
    "end_date": "2025-08-12"
  },
  "average_daily_food_groups": [
    {
      "food_group": "protein",
      "total_portions": 3.29,
      "dishes_count": 3,
      "main_dishes": ["Arroz con Pollo", "Huevo Cocido", "Huevos Revueltos", "Frijoles Guisados"]
    },
    {
      "food_group": "grains",
      "total_portions": 0.71,
      "dishes_count": 0,
      "main_dishes": ["Papas Cocidas"]
    }
  ],
  "food_group_diversity": 2,
  "recommendations": [
    "Add fresh fruits to provide vitamins, minerals, and fiber",
    "Include more vegetables for essential vitamins and minerals",
    "Include dairy products for calcium and protein",
    "Increase food group diversity to ensure balanced nutrition"
  ]
}
```

### 5.3 Obtener Análisis de Nutrientes

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/nutritional-analysis/nutrients/{schedule_id}
```

**Descripción**
Obtiene un análisis detallado del contenido nutricional de un horario de menú específico.

**200 Response body**
```json
{
  "menu_schedule_id": "68698ef4592f38947ff0a708",
  "menu_cycle_name": "Ciclo Básico Semanal",
  "analysis_period": {
    "start_date": "2025-08-06",
    "end_date": "2025-08-12"
  },
  "average_daily_nutrients": {
    "calories": 837.14,
    "protein": 54.29,
    "carbohydrates": 85.86,
    "fat": 30.86,
    "fiber": 0.0,
    "calcium": 0.0,
    "iron": 0.0,
    "vitamin_c": 0.0,
    "vitamin_a": 0.0
  },
  "macronutrient_distribution": {
    "protein_percentage": 25.9,
    "carbohydrate_percentage": 41.0,
    "fat_percentage": 33.1
  },
  "nutritional_adequacy_score": 35.0,
  "recommendations": [
    "Consider increasing portion sizes or adding more calorie-dense foods to meet energy needs",
    "Add more dairy products or calcium-rich foods like cheese, yogurt, or fortified foods",
    "Include iron-rich foods such as red meat, beans, or fortified cereals"
  ]
}
```

### 5.4 Comparar con Requerimientos Nutricionales

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/nutritional-analysis/comparison/{schedule_id}?age_group=school_age_6_12
```

**Parámetros Query**
- `age_group` (opcional): Grupo de edad para requerimientos nutricionales (school_age_6_12 o school_age_13_18, default: school_age_6_12)

**Descripción**
Compara el contenido nutricional real de un horario de menú con los requerimientos nutricionales estándar para diferentes grupos de edad.

**200 Response body**
```json
{
  "menu_schedule_id": "68698ef4592f38947ff0a708",
  "requirements": {
    "age_group": "school_age_6_12",
    "daily_calories": 1800.0,
    "daily_protein": 45.0,
    "daily_calcium": 1000.0,
    "daily_iron": 10.0,
    "daily_vitamin_c": 45.0,
    "daily_vitamin_a": 700.0
  },
  "actual_intake": {
    "total_calories": 837.14,
    "total_protein": 54.29,
    "total_carbohydrates": 85.86,
    "total_fat": 30.86,
    "total_fiber": 0.0,
    "total_calcium": 0.0,
    "total_iron": 0.0,
    "total_vitamin_c": 0.0,
    "total_vitamin_a": 0.0
  },
  "calorie_compliance": 46.51,
  "protein_compliance": 120.63,
  "calcium_compliance": 0.0,
  "iron_compliance": 0.0,
  "vitamin_c_compliance": 0.0,
  "vitamin_a_compliance": 0.0,
  "overall_compliance": 27.86,
  "compliance_status": "poor",
  "improvement_areas": [
    "Energy/Calories",
    "Calcium",
    "Iron",
    "Vitamin C",
    "Vitamin A"
  ],
  "recommendations": [
    "Consider increasing portion sizes or adding more calorie-dense foods to meet energy needs",
    "Add more dairy products or calcium-rich foods like cheese, yogurt, or fortified foods",
    "Include iron-rich foods such as red meat, beans, or fortified cereals",
    "Add fresh fruits to provide vitamins, minerals, and fiber",
    "Include more vegetables for essential vitamins and minerals"
  ]
}
```

### 5.5 Obtener Resumen Nutricional Simplificado

**Request URL**
```
GET http://127.0.0.1:8001/api/v1/nutritional-analysis/summary/{schedule_id}
```

**Descripción**
Obtiene un resumen simplificado del contenido nutricional para evaluación rápida.

**200 Response body**
```json
{
  "total_calories_per_day": 837.14,
  "total_protein_per_day": 54.29,
  "food_group_distribution": {
    "protein": 82.14,
    "grains": 17.86
  },
  "nutritional_balance_score": 35.0
}
```

---

## 6. Health Check

### 6.1 Estado General de la API

**Request URL**
```
GET http://127.0.0.1:8001/
```

**200 Response body**
```json
{
  "message": "Welcome to the PAE Menus API"
}
```

### 6.2 Verificación de Salud

**Request URL**
```
GET http://127.0.0.1:8001/health
```

**200 Response body**
```json
{
  "status": "healthy",
  "service": "PAE Menus API"
}
```

### 6.3 Verificación de Salud de Base de Datos

**Request URL**
```
GET http://127.0.0.1:8001/health/database
```

**200 Response body**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Códigos de Estado HTTP

- **200 OK**: Solicitud exitosa
- **400 Bad Request**: Datos de entrada inválidos
- **404 Not Found**: Recurso no encontrado
- **422 Unprocessable Entity**: Error de validación de datos
- **500 Internal Server Error**: Error interno del servidor

## Notas Importantes

1. **Formato de fechas**: Las fechas de entrada deben estar en formato ISO 8601 (YYYY-MM-DD)
2. **Paginación**: Todos los endpoints de listado soportan parámetros `skip` y `limit`
3. **Filtros**: Los filtros son opcionales y pueden combinarse
4. **IDs**: Los IDs de ingredientes, platos, ciclos de menú y horarios son strings de ObjectId de MongoDB
5. **Ubicaciones**: Las ubicaciones pueden ser `campus` o `town` según el tipo
6. **Estados**: Los recursos pueden tener diferentes estados (active/inactive, future/active/completed/cancelled)

## Autenticación

Actualmente la API no requiere autenticación, pero se recomienda implementar autenticación para uso en producción.

## CORS

La API permite solicitudes desde cualquier origen. Para producción, se recomienda configurar orígenes específicos. 