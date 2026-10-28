ENTITIES = {
    "item": {
        "label": "품목",
        "fields": [
            {"name": "name", "type": "str", "label": "이름", "required": True},
            {"name": "qty", "type": "int", "label": "수량", "default": 0},
            {"name": "min_qty", "type": "int", "label": "최소 수량", "default": 0},
            {"name": "unit", "type": "str", "label": "단위", "default": "개"}
        ]
    }
}
