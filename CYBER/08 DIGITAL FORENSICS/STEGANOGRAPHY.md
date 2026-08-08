Steganography is the art of hiding information in plain sight. It involves concealing a secret message within another, unsuspicious piece of media, such as an image, video, or even audio file.

The goal is to make the hidden data entirely undetectable to the naked eye or without specific tools. This technique differs from encryption, which scrambles the message itself but doesn't necessarily hide its existence.

There are different types of steganography depending on the medium used to hide the secret message. Here are the main categories:

| Type                     | Description                               | Techniques                                                                                                                                    |
| ------------------------ | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Text Steganography    | Hiding data within text files.            | - **Line shift**: Adding extra spaces or line breaks.  <br>- **Word shift**: Replacing words with synonyms.                                   |
| 2. Image Steganography   | Hiding data in digital images.            | - **LSB insertion**: Altering the least significant bit of pixel values.  <br>- **Palette modification**: Changing the image's color palette. |
| 3. Audio Steganography   | Embedding hidden messages in audio files. | - **Echo hiding**: Adding faint echoes.  <br>- **Spread spectrum**: Using unused audio frequencies.                                           |
| 4. Video Steganography   | Hiding data in video streams.             | - Embedding in **individual frames**.  <br>- Embedding in the **audio portion** of the video.                                                 |
| 5. Network Steganography | Concealing data within network traffic.   | - **Covert channels**: Using unused packet fields.  <br>- **Steganographic tunneling**: Encapsulating data in other protocols.                |

---
## Image Steganography


1. Prepare Files:
	Ensure you have an image file (`pic.jpg`) and the text file (`hidden.txt`) ready in the same directory.
2. Concatenate Files:
	- Open your terminal.
	- Navigate to the directory containing the files.
	- Use the following commands to concatenate the files in respective terminals:  
    - Using Windows Command Prompt (CMD):
	    `copy /b pic.jpg+hidden.txt new.jpg`
	- Using Ubuntu Terminal:
		`cat pic.jpg hidden.txt > new.jpg`
    - Using PowerShell:
	    `Get-Content pic.jpg, hidden.txt | Set-Content new.jpg`
3. Verify:
	- Check the directory for the newly created `new.jpg` file.
	- Open the file with an appropriate viewer (like an image viewer or text editor) to verify that the text file is hidden within the image.

