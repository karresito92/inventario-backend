\c inventario;

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    contrasenia VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS producto (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    marca VARCHAR(100),
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    estado VARCHAR(50),
    vendido BOOLEAN DEFAULT FALSE,
    imagen_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

CREATE INDEX idx_producto_vendido ON producto(vendido);
CREATE INDEX idx_producto_created ON producto(created_at);

CREATE TABLE IF NOT EXISTS pedido (
    id_pedido SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    completo BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id_detalle SERIAL PRIMARY KEY,
    id_pedido INTEGER NOT NULL REFERENCES pedido(id_pedido) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto) ON DELETE CASCADE,
    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
    precio_total DECIMAL(10,2) NOT NULL CHECK (precio_total >= 0)
);