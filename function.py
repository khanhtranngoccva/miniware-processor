import capa


command = ["capa.exe", "$file_name"]

try:
    output = capa.check_output(command, shell=True, text=True)
    print("capa output:")
    print(output)

except capa.CalledProcessError as e:
    print(f"Error: {e}")