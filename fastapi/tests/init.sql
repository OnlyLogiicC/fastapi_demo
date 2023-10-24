-- Enable the uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

INSERT INTO users (name,email,password,role) values ('superuser','mperez@oxyl.fr','$2b$12$81qp0AaMab2o9Ub9bKMM9emOvhanjwoPrt48d64W2GWM.JhUFavhO','super_admin');