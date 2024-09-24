import mysql.connector
from mysql.connector import Error

def connect_to_database():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',       # Change this if necessary
            user='root',   # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='EdC_bibliotheque'
        )
        if connection.is_connected():
            print("Connected to the database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def import_sql_file(connection, sql_file_path):
    """Import a .sql file into the MySQL database."""
    cursor = connection.cursor()
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
        for statement in sql_script.split(';'):
            if statement.strip():  # Avoid executing empty statements
                cursor.execute(statement)
        connection.commit()
        print("Database imported successfully.")
    except Exception as e:
        print(f"Error importing SQL file: {e}")
    finally:
        cursor.close()

def get_author_name(connection):
    author_id = input("Enter the author ID: ")
    query = "SELECT NomPlume FROM Auteur WHERE idAuteur = %s"
    cursor = connection.cursor()
    cursor.execute(query, (author_id,))
    author_name = cursor.fetchone()
    if author_name:
        # Decode the bytearray to a string
        print(f"Author's name: {author_name[0].decode('utf-8')}")
    else:
        print("No author found with that ID.")
    cursor.close()

def get_works_before_year(connection):
    year = input("Enter the year: ")
    query = "SELECT idOuvrage, AnneePremiereParution, TitreVO FROM Ouvrage WHERE AnneePremiereParution < %s"
    cursor = connection.cursor()
    cursor.execute(query, (year,))
    works = cursor.fetchall()
    if works:
        print("Works:")
        for work in works:
            # Decode the book name from bytearray to string if necessary
            book_name = work[2].decode('utf-8') if isinstance(work[2], bytes) else work[2]
            print(f"ID: {work[0]}, Date: {work[1]}, Name: {book_name.decode('utf-8')}")
    else:
        print("No works found.")
    cursor.close()

def get_works_by_type_and_style(connection):
    # Get and validate type ID
    type_id = input("Enter the type ID: ")
    # Check if type_id is a number
    if not type_id.isdigit():
        print("Invalid type ID. Please enter a valid number.")
        return
    
    # Get and validate style ID
    style_id = input("Enter the style ID: ")
    # Check if style_id is a number
    if not style_id.isdigit():
        print("Invalid style ID. Please enter a valid number.")
        return

    # Get and validate year inputs
    year1 = input("Enter year 1: ")
    year2 = input("Enter year 2: ")

    # Check if both year inputs are numbers
    if not (year1.isdigit() and year2.isdigit()):
        print("Invalid year inputs. Please enter valid numbers.")
        return

    # Prepare the SQL query
    query = """
    SELECT idOuvrage, TitreVO, AnneePremiereParution 
    FROM Ouvrage 
    WHERE idType = %s AND idStyle = %s 
    AND AnneePremiereParution BETWEEN %s AND %s
    """
    cursor = connection.cursor()
    cursor.execute(query, (type_id, style_id, year1, year2))
    works = cursor.fetchall()
    if works:
        print("Works of type T and style S published between the specified years:")
        for work in works:
            print(f"ID: {work[0]}, Title: {work[1].decode('utf-8')}, Year: {work[2]}")
    else:
        print("No works found.")
    cursor.close()

def delete_exemplaires_before_year(connection):
    year = input("Enter the year (YYYY): ")
    
    # Validate the year format
    if not (year.isdigit() and len(year) == 4):
        print("Invalid year format. Please enter a valid year in YYYY format.")
        return

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete exemplaires bought before {year}? (yes/no): ")
    if confirmation.lower() != 'yes':
        print("Deletion cancelled.")
        return

    cursor = connection.cursor()
    
    try:
        # First, delete related records from Emprunter
        delete_emprunter_query = """
        DELETE FROM Emprunter 
        WHERE idExemplaire IN (
            SELECT idExemplaire FROM Exemplaire WHERE dateAchat < %s
        )
        """
        # Use the first day of the year to compare
        first_day_of_year = f"{year}-01-01"
        cursor.execute(delete_emprunter_query, (first_day_of_year,))
        
        # Now, delete from Exemplaire
        delete_exemplaire_query = "DELETE FROM Exemplaire WHERE dateAchat < %s"
        cursor.execute(delete_exemplaire_query, (first_day_of_year,))
        
        connection.commit()
        print(f"Exemplaires bought before {year} and related emprunter records deleted.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()


def delete_works_by_author(connection):
    author_id = input("Enter the author ID: ")

    cursor = connection.cursor()
    
    try:
        # First, delete related records from Ecrire
        delete_ecrire_query = "DELETE FROM Ecrire WHERE idAuteur = %s"
        cursor.execute(delete_ecrire_query, (author_id,))
        
        # Now, delete from Ouvrage
        delete_ouvrage_query = """
        DELETE FROM Ouvrage 
        WHERE idOuvrage IN (SELECT idOuvrage FROM Ecrire WHERE idAuteur = %s)
        """
        cursor.execute(delete_ouvrage_query, (author_id,))
        
        connection.commit()
        print("Works and related authors deleted.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()




def main():
    connection = connect_to_database()
    if connection:
        while True:
            print("\nMenu:")
            print("1. Import SQL file")
            print("2. Get author's name")
            print("3. Get works published before a given year")
            print("4. Get works of a given type and style")
            print("5. Delete exemplaires bought before a date")
            print("6. Delete works written by an author")
            print("0. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                sql_file_path = input("Enter the path to the .sql file: ")
                import_sql_file(connection, sql_file_path)
            elif choice == '2':
                get_author_name(connection)
            elif choice == '3':
                get_works_before_year(connection)
            elif choice == '4':
                get_works_by_type_and_style(connection)
            elif choice == '5':
                delete_exemplaires_before_year(connection)
            elif choice == '6':
                delete_works_by_author(connection)
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

        connection.close()

if __name__ == "__main__":
    main()
