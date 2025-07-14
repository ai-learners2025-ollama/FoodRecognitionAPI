-- 建立資料表
CREATE TABLE food_nutrition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name_en TEXT NOT NULL,
    food_name_zh TEXT NOT NULL,
    calories REAL NOT NULL DEFAULT 0,
    protein REAL NOT NULL DEFAULT 0,
    carbs REAL NOT NULL DEFAULT 0,
    is_ident BOOLEAN NOT NULL DEFAULT 1,
    create_user TEXT NOT NULL,
    create_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_user TEXT NOT NULL,
    update_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 建立資料表
CREATE TABLE identification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name NVARCHAR(50) NOT NULL,
    image_path NVARCHAR(255) NOT NULL,
    ident_image_name NVARCHAR(50),
    ident_content NVARCHAR(200),
    create_user NVARCHAR(20) NOT NULL,
    create_ip NVARCHAR(20) NOT NULL,
    create_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name NVARCHAR(50) NOT NULL,
    model_path NVARCHAR(50) NOT NULL,
    model_ident_items NVARCHAR(1000) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT 1,
    memo NVARCHAR(1000),
    create_user NVARCHAR(20) NOT NULL,
    create_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_user NVARCHAR(20) NOT NULL,
    update_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
