TASKS = [
    {
        "name": "easy_syntax_fix",
        "difficulty": "easy",
        "description": "Fix basic JSON syntax error: trailing comma",
        "broken_json": '{"name": "Alice", "age": 30, "email": "alice@example.com",}',
        "correct_json": '{"name": "Alice", "age": 30, "email": "alice@example.com"}',
        "schema": {
            "type": "object",
            "required": ["name", "age", "email"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "email": {"type": "string"}
            }
        },
        "hint": "Check for trailing commas before closing braces or brackets"
    },
    {
        "name": "medium_type_repair",
        "difficulty": "medium",
        "description": "Fix wrong field types and add missing required field",
        "broken_json": '{"user": "Bob", "score": "95", "active": "true"}',
        "correct_json": '{"user": "Bob", "score": 95, "active": true, "role": "user"}',
        "schema": {
            "type": "object",
            "required": ["user", "score", "active", "role"],
            "properties": {
                "user": {"type": "string"},
                "score": {"type": "number"},
                "active": {"type": "boolean"},
                "role": {"type": "string", "enum": ["admin", "user", "guest"]}
            }
        },
        "hint": "score should be a number not string, active should be boolean not string, role field is missing"
    },
    {
        "name": "hard_nested_reconstruction",
        "difficulty": "hard",
        "description": "Reconstruct heavily corrupted nested JSON with unquoted keys and wrong types",
        "broken_json": "{product: 'Laptop', price: '999.99', specs: {ram: '16gb', storage: 512}}",
        "correct_json": '{"product": "Laptop", "price": 999.99, "specs": {"ram": "16GB", "storage": 512}, "available": true}',
        "schema": {
            "type": "object",
            "required": ["product", "price", "specs", "available"],
            "properties": {
                "product": {"type": "string"},
                "price": {"type": "number"},
                "available": {"type": "boolean"},
                "specs": {
                    "type": "object",
                    "required": ["ram", "storage"],
                    "properties": {
                        "ram": {"type": "string"},
                        "storage": {"type": "number"}
                    }
                }
            }
        },
        "hint": "Quote all keys, fix price to number, add available field, normalize ram to uppercase, keep storage as number"
    }
]
