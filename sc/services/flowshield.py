# Placeholder for rate limiting logic
# In a real system, this might use a more sophisticated mechanism like Redis,
# distributed counters, or a dedicated rate-limiting service.

# Define a simple threshold for demonstration purposes
MAX_REQUESTS_PER_WINDOW = 100  # Example: 100 requests allowed
# Window duration is implicitly handled by how `request_count` is managed by the caller.

def is_under_attack(ip: str, request_count: int) -> bool:
    """
    Checks if the given IP is making too many requests based on a simple count.

    Args:
        ip (str): The IP address of the client.
        request_count (int): The number of requests observed from this IP
                             within the current tracking window.

    Returns:
        bool: True if the request count exceeds the defined threshold (potential attack),
              False otherwise.
    """
    # Simple check: if request_count exceeds the threshold, consider it an attack.
    # The 'ip' argument is included for future enhancements (e.g., per-IP thresholds, logging).
    if request_count > MAX_REQUESTS_PER_WINDOW:
        print(f"Rate limit exceeded for IP {ip}: {request_count} requests > {MAX_REQUESTS_PER_WINDOW}")
        return True
    return False

if __name__ == '__main__':
    # Example Usage
    ip_address = "192.168.1.100"

    # Simulate request counts
    counts_to_test = [10, 50, 100, 101, 150]

    for count in counts_to_test:
        under_attack = is_under_attack(ip_address, count)
        if under_attack:
            print(f"IP: {ip_address}, Count: {count} -> Under Attack: YES")
        else:
            print(f"IP: {ip_address}, Count: {count} -> Under Attack: NO")

    # Example with a different IP
    another_ip = "203.0.113.45"
    if not is_under_attack(another_ip, 20):
        print(f"\nIP: {another_ip}, Count: 20 -> Under Attack: NO (as expected)")

    if is_under_attack(another_ip, 200):
        print(f"IP: {another_ip}, Count: 200 -> Under Attack: YES (as expected)")
