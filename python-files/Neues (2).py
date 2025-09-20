# 7DTD Koordinaten → Region Finder

def koords_to_region(x, z):
    # Größe einer Region in Blocks (Standard: 512)
    region_size = 512
    
    # Bestimme Region Index
    rx = x // region_size
    rz = z // region_size
    
    # rr-Dateiname (zweistellig, mit führender Null)
    region_name = f"rr{rx:02d}{rz:02d}"
    
    return region_name

# Beispiel
x = int(input("X-Koordinate: "))
z = int(input("Z-Koordinate: "))

region = koords_to_region(x, z)
print(f"Die Koordinaten ({x},{z}) liegen in der Region: {region}")
