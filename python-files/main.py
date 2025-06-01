import os
import subprocess
import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

# DigitalOcean Spaces Setup.
session = boto3.session.Session()
client = session.client('s3',
                        region_name=os.getenv("DO_REGION_NAME"),
                        endpoint_url=os.getenv("DO_ENDPOINT_URL"),
                        aws_access_key_id=os.getenv("DO_KEY_ID"),
                        aws_secret_access_key=os.getenv("DO_SECRET_ID")
                        )    
BUCKET_NAME = os.getenv('BUCKET_NAME')
if not BUCKET_NAME:
    raise ValueError("❌ BUCKET_NAME is not set. Check your .env file.")

def encode(input_video,output_name,selected_quality,quality,scale,crf,bv,maxrate,bufsize):
    file_compress = f'{output_name}_compress.mp4'
    
    command = f'ffmpeg -i {input_video} -vf "scale=-2:{scale}" -c:v libx264 -crf 23 -preset fast -c:a copy {quality}'
    command_gpu = f'ffmpeg -i "{input_video}" -vf "scale=640:480" -c:v h264_nvenc -b:v {bv}k -maxrate {maxrate}k -bufsize {bufsize}k -c:a aac -b:a 128k "{quality}"'
    command_compress = f'ffmpeg -i {input_video} -vcodec libx265 -crf 30 -preset fast -tag:v hvc1 -acodec aac -b:a 128k {file_compress}'
    try:
        if selected_quality == 0: 
            subprocess.run(command_gpu,check=True, 
                            stderr=subprocess.PIPE, 
                            universal_newlines=True);
            file_size = os.path.getsize(quality)
            print("\n" + "="*50)
            print("✅ Wait File being uploading to server!")
            file_basename = os.path.basename(quality)
            client.upload_file(f'{quality}', BUCKET_NAME, f'upload/{file_basename}')
            client.put_object_acl(ACL='public-read',Bucket=BUCKET_NAME,Key=f'upload/{file_basename}')
            print("✅ Conversion Successful!")
            print(f"Generated Files: \n{quality}: {file_size/(1024*1024):.2f} MB")
            print(f'Generated File link: https://{BUCKET_NAME}.blr1.digitaloceanspaces.com/upload/{file_basename}')
            os.remove(quality)
            print("="*50)
            
        elif selected_quality == 4:
            subprocess.run(command_compress,check=True,
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
            size_compress = os.path.getsize(file_compress)
            print("\n" + "="*50)
            print("✅ Compression Successful!")
            print("✅ Wait File being uploading to server!")
            file_basename = os.path.basename(quality)
            client.upload_file(f'{file_compress}', BUCKET_NAME, f'upload/{file_basename}')
            client.put_object_acl(ACL='public-read',Bucket=BUCKET_NAME,Key=f'upload/{file_basename}')
            print(f"Generated Files: \n{file_compress}: {size_compress/(1024*1024):.2f} MB")
            print(f'Generated File link: https://{BUCKET_NAME}.blr1.digitaloceanspaces.com/upload/{file_basename}')
            os.remove(file_compress)
            print("="*50)
        else:
            subprocess.run(command,check=True, 
                            stderr=subprocess.PIPE, 
                            universal_newlines=True);
            file_size = os.path.getsize(quality)
            print("\n" + "="*50)
            print("✅ Wait File being uploading to server!")
            file_basename = os.path.basename(quality)
            client.upload_file(f'{quality}', BUCKET_NAME, f'upload/{file_basename}')
            client.put_object_acl(ACL='public-read',Bucket=BUCKET_NAME,Key=f'upload/{file_basename}')
            print("✅ Conversion Successful!")
            print(f"Generated Files: \n{quality}: {file_size/(1024*1024):.2f} MB")
            print(f'Generated File link: https://{BUCKET_NAME}.blr1.digitaloceanspaces.com/upload/{file_basename}')
            os.remove(quality)
            print("="*50)
                
    except subprocess.CalledProcessError as e:
        print("\n" + "="*50)
        print("❌ Conversion Failed!")
        print(f"Error: {e.stderr.splitlines()[-1] if e.stderr else 'Unknown error'}")
        print("="*50)
    except FileNotFoundError:
        print("\nError: FFmpeg not found. Please install FFmpeg first.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")

def main():
    input_video = input('Enter Video address:')
    output_name = input("Enter video name:")
    selected_quality = int(input("Enter Number Which Quality To convert: \n 0 for Gpu Mode \n 1 for 480 \n 2 for 720 \n 3 for 1080 \n 4 for compression \nWhat you want? :"))
    file_480 = f'{output_name}_480.mp4'
    file_720 = f'{output_name}_720.mp4'
    file_1080 = f'{output_name}_1080.mp4'
    file_compress = f'{output_name}_compress.mp4'
    
    if selected_quality == 0:
        choice = int(input("Which You Want:\nEnter 1 For 480\nEnter 2 for 720\nEnter 3 for 1080\nEnter Your Choice:"))
        if choice == 1:
            encode(input_video,output_name,selected_quality,quality=file_480,scale=480,crf=26,bv=1000,maxrate=2000,bufsize=2000)
        elif choice == 2:
            encode(input_video,output_name,selected_quality,quality=file_720,scale=720,crf=23,bv=2000,maxrate=4000,bufsize=4000)
        elif choice == 3:
            encode(input_video,output_name,selected_quality,quality=file_1080,scale=1080,crf=20,bv=3000,maxrate=6000,bufsize=6000)
    elif selected_quality == 1:
        encode(input_video,output_name,selected_quality,quality=file_480,scale=480,crf=None,bv=None,maxrate=None,bufsize=None)
    elif selected_quality == 2:
        encode(input_video,output_name,selected_quality,quality=file_720,scale=720,crf=None,bv=None,maxrate=None,bufsize=None)
    elif selected_quality == 3:
        encode(input_video,output_name,selected_quality,quality=file_1080,scale=1080,crf=None,bv=None,maxrate=None,bufsize=None)
    elif selected_quality == 4:
        encode(input_video,output_name,selected_quality,quality=file_compress,scale=None,crf=None,bv=None,maxrate=None,bufsize=None)

if __name__ == "__main__":
    main()