-- ============================================
-- PrismaVitae - Schema de Base de Datos
-- Supabase (PostgreSQL)
-- Ejecutar desde el SQL Editor de Supabase.
-- ============================================

-- ============================================
-- Tabla de Candidatos (CVs y Cédulas escaneados con IA)
-- Permite fusión: un candidato puede tener datos de CV y de cédula
-- ============================================
CREATE TABLE IF NOT EXISTS candidatos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre VARCHAR(255),
  telefono VARCHAR(50),
  email VARCHAR(255),
  habilidades JSONB DEFAULT '[]',
  experiencia_anios FLOAT,
  educacion VARCHAR(500),
  resumen TEXT,
  archivo_url VARCHAR(500),
  datos_crudos JSONB,
  confianza FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de Propuestas (Ruth Julio De Camps)
CREATE TABLE IF NOT EXISTS propuestas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  no INTEGER NOT NULL,
  reg_dist VARCHAR(100),
  cedula VARCHAR(20) NOT NULL,
  nombre_completo VARCHAR(255) NOT NULL,
  sexo VARCHAR(20),
  cargo_solicitado VARCHAR(255),
  cargo_aprobado VARCHAR(255),
  escolaridad VARCHAR(255),
  en_sustitucion_de VARCHAR(255),
  cedula_no VARCHAR(20),
  fecha_ingreso DATE,
  centro VARCHAR(255),
  referido_por VARCHAR(255),
  telefono VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de Reajustes Salariales
CREATE TABLE IF NOT EXISTS reajustes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  cedula VARCHAR(20) NOT NULL,
  nombre_completo VARCHAR(255) NOT NULL,
  grupo_ocupacional VARCHAR(255),
  cargo VARCHAR(255),
  salario_actual FLOAT DEFAULT 0,
  salario_solicitado FLOAT DEFAULT 0,
  observacion VARCHAR(1000),
  diferencia_salarial FLOAT DEFAULT 0,
  porcentaje_incremento FLOAT DEFAULT 0,
  fecha_efectividad DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de No Proceden
CREATE TABLE IF NOT EXISTS no_proceden (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  no INTEGER NOT NULL,
  reg_dist VARCHAR(100),
  cedula VARCHAR(20) NOT NULL,
  nombre_completo VARCHAR(255) NOT NULL,
  sexo VARCHAR(20),
  cargo_solicitado VARCHAR(255),
  salario_solicitado FLOAT DEFAULT 0,
  escolaridad VARCHAR(255),
  observacion VARCHAR(1000),
  referido_por VARCHAR(255),
  telefono VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Tabla de Perfiles de Usuario (Auth)
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  status VARCHAR(50) DEFAULT 'pending',
  permissions JSONB DEFAULT '["ver_propuestas", "ver_reajustes", "ver_no_proceden", "ver_candidatos"]',
  full_name VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Storage: bucket "cvs" (público) para CVs y cédulas
-- ============================================
INSERT INTO storage.buckets (id, name, public)
VALUES ('cvs', 'cvs', true)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- Habilitar RLS (Row Level Security)
-- ============================================
ALTER TABLE candidatos ENABLE ROW LEVEL SECURITY;
ALTER TABLE propuestas ENABLE ROW LEVEL SECURITY;
ALTER TABLE reajustes ENABLE ROW LEVEL SECURITY;
ALTER TABLE no_proceden ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- ============================================
-- Políticas de acceso (desarrollo)
-- Permitir todas las operaciones para usuarios anónimos.
-- La autorización real se delega a la capa FastAPI.
-- ============================================
DROP POLICY IF EXISTS "Allow all for candidatos" ON candidatos;
DROP POLICY IF EXISTS "Allow all for propuestas" ON propuestas;
DROP POLICY IF EXISTS "Allow all for reajustes" ON reajustes;
DROP POLICY IF EXISTS "Allow all for no_proceden" ON no_proceden;

CREATE POLICY "Allow all for candidatos" ON candidatos FOR ALL USING (true);
CREATE POLICY "Allow all for propuestas" ON propuestas FOR ALL USING (true);
CREATE POLICY "Allow all for reajustes" ON reajustes FOR ALL USING (true);
CREATE POLICY "Allow all for no_proceden" ON no_proceden FOR ALL USING (true);

-- Políticas para user_profiles
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Service role can manage all profiles" ON user_profiles;

CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Service role can manage all profiles" ON user_profiles FOR ALL USING (true);

-- ============================================
-- Índices para mejorar rendimiento
-- ============================================
CREATE INDEX IF NOT EXISTS idx_candidatos_email ON candidatos(email);
CREATE INDEX IF NOT EXISTS idx_candidatos_nombre ON candidatos(nombre);
CREATE INDEX IF NOT EXISTS idx_propuestas_cedula ON propuestas(cedula);
CREATE INDEX IF NOT EXISTS idx_reajustes_cedula ON reajustes(cedula);
CREATE INDEX IF NOT EXISTS idx_no_proceden_cedula ON no_proceden(cedula);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);