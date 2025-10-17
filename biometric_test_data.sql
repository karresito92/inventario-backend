-- Datos de prueba para tabla biometric_data

-- 1. Registro de reconocimiento facial
INSERT INTO biometric_data (
    id,
    user_id,
    biometric_type,
    encrypted_data,
    hash,
    quality_score,
    is_active,
    device_info,
    created_at,
    updated_at
) VALUES (
    uuid_generate_v4(),
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'facial',
    '\x89504e470d0a1a0a0000000d494844520000010',  -- Datos encriptados simulados
    '5d41402abc4b2a76b9719d911017c592',
    0.95,
    TRUE,
    '{"model": "iPhone 14 Pro", "os": "iOS 16.5", "sensor": "Face ID"}',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 2. Registro de huella dactilar (dedo índice derecho)
INSERT INTO biometric_data (
    id,
    user_id,
    biometric_type,
    encrypted_data,
    hash,
    quality_score,
    is_active,
    device_info,
    created_at,
    updated_at
) VALUES (
    uuid_generate_v4(),
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'fingerprint',
    '\xffd8ffe000104a46494600010101006000600000',  -- Datos encriptados simulados
    'e4d909c290d0fb1ca068ffaddf22cbd0',
    0.88,
    TRUE,
    '{"model": "Samsung Galaxy S23", "os": "Android 13", "sensor": "Ultrasonic"}',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 3. Registro de huella dactilar desactivado (dedo pulgar)
INSERT INTO biometric_data (
    id,
    user_id,
    biometric_type,
    encrypted_data,
    hash,
    quality_score,
    is_active,
    device_info,
    created_at,
    updated_at
) VALUES (
    uuid_generate_v4(),
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'fingerprint',
    '\x424d3e000000000000003e000000280000',  -- Datos encriptados simulados
    'a3c65c2974270fd093ee8a9bf8ae7d0b',
    0.72,
    FALSE,  -- Desactivado
    '{"model": "Samsung Galaxy S23", "os": "Android 13", "sensor": "Ultrasonic"}',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 4. Registro de iris (calidad baja, pendiente de re-captura)
INSERT INTO biometric_data (
    id,
    user_id,
    biometric_type,
    encrypted_data,
    hash,
    quality_score,
    is_active,
    device_info,
    created_at,
    updated_at
) VALUES (
    uuid_generate_v4(),
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'iris',
    '\x504b030414000600080000002100',  -- Datos encriptados simulados
    'b17ef6d19c7a5b1ee83b907c595526dc',
    0.45,  -- Calidad baja
    TRUE,
    '{"model": "Tablet Pro", "os": "Windows 11", "sensor": "IR Camera"}',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 5. Registro de voz (sin quality_score)
INSERT INTO biometric_data (
    id,
    user_id,
    biometric_type,
    encrypted_data,
    hash,
    quality_score,
    is_active,
    device_info,
    created_at,
    updated_at
) VALUES (
    uuid_generate_v4(),
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'voice',
    '\x52494646240800005741564566',  -- Datos encriptados simulados
    'c81e728d9d4c2f636f067f89cc14862c',
    NULL,  -- Sin score de calidad
    TRUE,
    '{"model": "Google Pixel 7", "os": "Android 14", "microphone": "Built-in"}',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);