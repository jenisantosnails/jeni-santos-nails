from sqlalchemy import text

from database.database import engine


def migrate():
    print("Iniciando atualização da tabela appointments...")

    with engine.begin() as connection:
        columns = connection.execute(
            text("PRAGMA table_info(appointments)")
        ).fetchall()

        existing_columns = {
            column[1]
            for column in columns
        }

        if "return_type" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN return_type VARCHAR(20)
                    """
                )
            )
            print("Coluna return_type adicionada.")
        else:
            print("Coluna return_type já existe.")

        if "return_date" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN return_date DATETIME
                    """
                )
            )
            print("Coluna return_date adicionada.")
        else:
            print("Coluna return_date já existe.")

        if "completed_at" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN completed_at DATETIME
                    """
                )
            )
            print("Coluna completed_at adicionada.")
        else:
            print("Coluna completed_at já existe.")

        if "reminder_sent_at" not in existing_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN reminder_sent_at DATETIME
                    """
                )
            )
            print("Coluna reminder_sent_at adicionada.")
        else:
            print("Coluna reminder_sent_at já existe.")

    print("Migração concluída com sucesso!")


if __name__ == "__main__":
    migrate()