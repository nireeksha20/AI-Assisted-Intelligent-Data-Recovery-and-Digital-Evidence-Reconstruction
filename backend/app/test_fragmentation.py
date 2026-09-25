from core.fragment_simulator import create_fragmented_storage


result = create_fragmented_storage(
    r"C:\Users\H P\Pictures\MCE_Logo.jpeg",
    output_path="samples/fragmented_storage.bin",
    metadata_path="samples/fragment_metadata.json",
    fragment_size=4096,
    noise_blocks=8,
    seed=42,
)


print("\nFragmentation completed!")

print("\nOriginal file:")
print(result["original_file"])

print("Original size:")
print(result["original_size_bytes"], "bytes")

print("\nFragments:")
print(result["fragment_count"])

print("\nNoise blocks:")
print(result["noise_blocks"])

print("\nTotal storage blocks:")
print(result["storage_block_count"])

print("\nStorage size:")
print(result["storage_size_bytes"], "bytes")