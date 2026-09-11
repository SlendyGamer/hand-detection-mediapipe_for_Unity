import cv2
import mediapipe as mp
import numpy as np
import math


def run_calibration(camera_index=None):
    # === CONFIGURAÇÃO ===

    if camera_index is None:
        try:
            from config_gui import get_camera_index
            camera_index = get_camera_index()
        except Exception:
            camera_index = 0

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.8)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        # fallback sem backend explícito
        cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Erro: não foi possível abrir a câmera índice {camera_index}.")
        hands.close()
        return None

    print(f"Calibração usando câmera índice {camera_index}")

    # === DADOS DE CALIBRAÇÃO ===
    start_cm = 20
    step_cm = 5
    end_cm = 100
    distances_cm = list(range(start_cm, end_cm + 1, step_cm))  # [20, 25, ..., 100]
    current_index = 0
    pixels_list = []
    cm_list = []

    print("INICIANDO CALIBRAÇÃO AUTOMÁTICA")
    print(f"Distâncias: {distances_cm}")
    print("Posicione a mão na distância indicada e pressione 's'\n")

    result = None

    calibrating = True
    pending_input = False
    current_pixels = 0.0

    while calibrating and current_index < len(distances_cm):
        ret, frame = cap.read()
        if not ret:
            print("Erro: Câmera não disponível.")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        target_cm = distances_cm[current_index]
        display_text = f"PROXIMA: {target_cm} cm | Salvos: {len(pixels_list)}/{len(distances_cm)}"

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            x1 = lm[5].x * image.shape[1]
            y1 = lm[5].y * image.shape[0]
            x2 = lm[17].x * image.shape[1]
            y2 = lm[17].y * image.shape[0]

            current_pixels = math.hypot(x2 - x1, y2 - y1)

            # Desenha pontos
            cv2.circle(image, (int(x1), int(y1)), 12, (0, 255, 0), -1)
            cv2.circle(image, (int(x2), int(y2)), 12, (0, 0, 255), -1)
            cv2.putText(image, f'Pixels: {current_pixels:.1f}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            display_text = f"{target_cm} cm → Pixels: {current_pixels:.1f} | 's' para salvar"

        # Texto grande no centro
        cv2.putText(image, f"{target_cm} cm", (image.shape[1] // 2 - 100, image.shape[0] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 255), 4)

        cv2.putText(image, display_text, (10, image.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('CALIBRACAO AUTOMATICA - S: salvar', image)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('s'), ord('S')) and results.multi_hand_landmarks:
            print(f"\nSALVANDO: {current_pixels:.1f} px → {target_cm} cm")
            pixels_list.append(current_pixels)
            cm_list.append(target_cm)
            current_index += 1
            print(f"Próxima: {distances_cm[current_index] if current_index < len(distances_cm) else 'CONCLUÍDO'} cm")

        elif key in (ord('q'), ord('Q'), 27):
            print("Calibração interrompida pelo usuário.")
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

    # === CÁLCULO DOS COEFICIENTES ===
    if len(pixels_list) >= 3:
        coff = np.polyfit(pixels_list, cm_list, 2)
        A, B, C = coff
        print("\n" + "=" * 70)
        print("CALIBRAÇÃO CONCLUÍDA COM SUCESSO")
        print(f"Pontos coletados: {len(pixels_list)}")
        print(f"A = {A:.6e}")
        print(f"B = {B:.6f}")
        print(f"C = {C:.6f}")
        # print(f"\nSUBSTITUA NO SEU CÓDIGO:")
        # print(f"coff = np.array([{A:.6e}, {B:.6f}, {C:.6f}])")
        # print("="*70)
        result = (float(A), float(B), float(C))
    else:
        print(f"\nCalibração incompleta: {len(pixels_list)} pontos coletados.")

    return result


if __name__ == "__main__":
    run_calibration()
