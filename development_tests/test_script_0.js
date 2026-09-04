window.onerror = function(msg, url, lineNo, columnNo, error) {
      console.warn("Handled gracefully:", msg);
      return true; // prevents browser freeze
    };