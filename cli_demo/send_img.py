import socket
import pickle
import struct
import cv2


def send_image(image_path, server_ip="127.0.0.1", server_port=5000):
    """Envía una imagen al servidor y recibe la respuesta."""
    try:
        with open(image_path, "rb") as f:
            img_data = f.read()

        with socket.create_connection((server_ip, server_port)) as sock:
            # Enviar la longitud de la imagen
            sock.sendall(struct.pack("!I", len(img_data)))
            # Enviar la imagen
            sock.sendall(img_data)

            # Recibir la longitud de la respuesta
            data = sock.recv(4)
            result_size = struct.unpack("!I", data)[0]

            # Recibir la imagen procesada
            result_data = b""
            while len(result_data) < result_size:
                result_data += sock.recv(result_size - len(result_data))

        # Guardar la imagen procesada
        with open("processed_image.jpg", "wb") as f:
            f.write(result_data)
        print("Imagen procesada guardada como 'processed_image.jpg'.")

    except Exception as e:
        print(f"Error: {e}")


def recv_exact(sock, n):
    """Receive exactly `n` bytes from the socket."""
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed before receiving all data")
        data += chunk
    return data


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    with socket.create_connection(("127.0.0.1", 5000)) as sock:
        builder = pickle.dumps({
            "model_name": "inverter",
            "model_kwargs": {}
        })
        sock.sendall(struct.pack("!I", len(builder)))
        sock.sendall(builder)
        while True:
            ret, img = cap.read()
            if ret:
                data = pickle.dumps(img)
                sock.sendall(struct.pack("!I", len(data)))
                sock.sendall(data)

                rdata = recv_exact(sock, 4)
                size = struct.unpack("!I", rdata)[0]
                rdata = recv_exact(sock, size)

                rimg = pickle.loads(rdata)
                cv2.imshow("Inverted", rimg)
                x = cv2.waitKey(1) & 0xFF
                if x == ord("q"):
                    break

            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    cv2.destroyAllWindows()
