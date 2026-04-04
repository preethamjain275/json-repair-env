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
    },
    {
        "name": "extreme_multilevel_repair",
        "difficulty": "extreme",
        "description": "Fix deeply nested JSON with broken arrays, unquoted keys, and missing commas",
        "broken_json": "{'order_id': 1001, customer: { 'id': 'C-123', name: 'John Doe', contact: ['john@example.com', 1234567890 ] }, items: [ { sku: 'IT-01', qty: 2 price: 19.99 } { sku: 'IT-02', qty: 1, price: '45.00'}]",
        "correct_json": '{"order_id": 1001, "customer": {"id": "C-123", "name": "John Doe", "contact": ["john@example.com", "1234567890"]}, "items": [{"sku": "IT-01", "qty": 2, "price": 19.99}, {"sku": "IT-02", "qty": 1, "price": 45.00}]}',
        "schema": {
            "type": "object",
            "required": ["order_id", "customer", "items"],
            "properties": {
                "order_id": {"type": "integer"},
                "customer": {
                    "type": "object",
                    "required": ["id", "name", "contact"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "contact": {"type": "array"}
                    }
                },
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["sku", "qty", "price"]
                    }
                }
            }
        },
        "hint": "Fix missing commas in the items array, quote all keys, ensure consistent contact types, and convert item prices to numbers."
    },
    {
        "name": "chaos_malformed_object",
        "difficulty": "chaos",
        "description": "Repair a chaotic object with mismatched brackets, unquoted text, and significant structural damage",
        "broken_json": "{ system_log: version: 2.0, events: [ { timestamp: 1700000000 level: ERROR msg: 'Auth failed' }, type: 'connection', info: { ip: 192.168.1.1, retry: true } status: 'FAIL' ",
        "correct_json": '{"system_log": {"version": "2.0", "events": [{"timestamp": 1700000000, "level": "ERROR", "msg": "Auth failed"}], "type": "connection", "info": {"ip": "192.168.1.1", "retry": true}, "status": "FAIL"}}',
        "schema": {
            "type": "object",
            "required": ["system_log"],
            "properties": {
                "system_log": {
                    "type": "object",
                    "required": ["version", "events", "type", "info", "status"]
                }
            }
        },
        "hint": "The events array is missing a closing bracket, the system_log structure is flat in the broken version but needs nesting, and multiple delimiters are missing."
    },
    {
        "name": "mixed_quote_nightmare",
        "difficulty": "hard",
        "description": "Fix a JSON containing mixed single quotes, double quotes, and unquoted keys",
        "broken_json": "{ \"title\": 'The Matrix', director: \"Wachowskis\", 'year': 1999, casting: [ 'Keanu', \"Laurence\", Carrie-Anne ] }",
        "correct_json": '{"title": "The Matrix", "director": "Wachowskis", "year": 1999, "casting": ["Keanu", "Laurence", "Carrie-Anne"]}',
        "schema": {
          "type": "object",
          "required": ["title", "director", "year", "casting"]
        },
        "hint": "Ensure all keys and string values use double quotes, and handle unquoted array elements."
    },
    {
        "name": "escaped_character_confusion",
        "difficulty": "extreme",
        "description": "Repair JSON with malformed escape sequences and control characters",
        "broken_json": '{"path": "C:\\\\Users\\\\Admin\\\\Documents", "message": "Line 1\\nLine 2\\tTabbed", "regex": "\\\d+\\\\\\.js"}',
        "correct_json": '{"path": "C:\\\\Users\\\\Admin\\\\Documents", "message": "Line 1\\nLine 2\\tTabbed", "regex": "\\\\d+\\\\\\\\.js"}',
        "schema": {
            "type": "object",
            "required": ["path", "message", "regex"]
        },
        "hint": "Handle backslash escaping correctly for Windows paths and Regex strings."
    },
    {
        "name": "truncated_stream_recovery",
        "difficulty": "chaos",
        "description": "Recover data from a JSON object that was truncated mid-transmission",
        "broken_json": '{"sensor_id": "WS-092", "readings": [ {"t": 171221, "v": 24.5}, {"t": 171222, "v": 24.6}, {"t": 171223, ',
        "correct_json": '{"sensor_id": "WS-092", "readings": [{"t": 171221, "v": 24.5}, {"t": 171222, "v": 24.6}]}',
        "schema": {
            "type": "object",
            "required": ["sensor_id", "readings"]
        },
        "hint": "The JSON ends abruptly. You must close the open object and array, discarding the partial element if necessary."
    },
    {
        "name": "deep_recursive_reconstruction",
        "difficulty": "extreme",
        "description": "Repair a deep hierarchy (5+ levels) with inconsistent naming and missing braces",
        "broken_json": "{ a: { b: { c: { d: { e: 'val', f: 10 } g: [1 2 3] h: { i: j } } } } }",
        "correct_json": '{"a": {"b": {"c": {"d": {"e": "val", "f": 10, "g": [1, 2, 3], "h": {"i": "j"}}}}}}',
        "schema": { "type": "object", "required": ["a"] },
        "hint": "Track nesting levels carefully to ensure every opening brace has a matching closing brace."
    },
    {
        "name": "data_type_normalization",
        "difficulty": "medium",
        "description": "Convert inconsistent data formats (dates, booleans in strings) to standard JSON types",
        "broken_json": '{"active": "YES", "count": "42", "verified": 0, "tags": "web,app,json"}',
        "correct_json": '{"active": true, "count": 42, "verified": false, "tags": ["web", "app", "json"]}',
        "schema": {
            "type": "object",
            "required": ["active", "count", "verified", "tags"],
            "properties": {
                "active": {"type": "boolean"},
                "count": {"type": "integer"},
                "verified": {"type": "boolean"},
                "tags": {"type": "array"}
            }
        },
        "hint": "Normalize 'YES' to true, '42' to integer 42, 0 to false, and the comma-separated string to an array."
    }
]
