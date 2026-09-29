from AgentLoader import loader

def test_loader():
    try:
        response = loader()

        print("\n========== AGENT LOADER TEST ==========")

        print(f"[TEST] Models loaded: {len(response['models'])}")

        for model in response["models"]:
            print(f"       - {model}")

        print(f"[TEST] Database: {response['database']}")
        print(f"[TEST] Context size: {response['context_size']}")

        print("========== TEST PASSED ==========\n")

        return response

    except Exception as e:
        print("\n========== AGENT LOADER TEST FAILED ==========")
        print(f"[TEST] {e}")
        print("==============================================\n")
        return None


if __name__ == "__main__":
    test_loader()
