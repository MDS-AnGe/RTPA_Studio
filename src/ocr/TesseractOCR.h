/**
 * OCR Engine natif avec Tesseract + OpenCV
 * Remplacement complet du système Python pytesseract
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <opencv2/opencv.hpp>
#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>

#include "types/PokerTypes.h"

namespace rtpa::ocr {

/**
 * Configuration préprocessing OpenCV
 */
struct PreprocessConfig {
    // Filtrage et amélioration
    bool useGaussianBlur = true;
    double blurSigma = 1.0;
    
    bool useBilateralFilter = true;
    int bilateralD = 9;
    double bilateralSigmaColor = 75.0;
    double bilateralSigmaSpace = 75.0;
    
    // Binarisation
    bool useAdaptiveThreshold = true;
    double adaptiveMaxValue = 255.0;
    int adaptiveMethod = cv::ADAPTIVE_THRESH_GAUSSIAN_C;
    int adaptiveThresholdType = cv::THRESH_BINARY;
    int adaptiveBlockSize = 11;
    double adaptiveC = 2.0;
    
    // Morphologie
    bool useMorphology = true;
    int morphKernelSize = 3;
    int morphIterations = 1;
    
    // Redimensionnement
    bool useResize = true;
    double resizeScale = 2.0;
    int resizeInterpolation = cv::INTER_CUBIC;
    
    // Contraste et luminosité
    bool useContrastEnhancement = true;
    double alpha = 1.5; // contraste
    double beta = 30;   // luminosité
};

/**
 * Résultat OCR avec métadonnées
 */
struct OCRResult {
    std::string text;
    float confidence = 0.0f;
    cv::Rect boundingBox;
    std::vector<cv::Point> wordBoundaries;
    
    // Timing
    double preprocessTime = 0.0;
    double recognitionTime = 0.0;
    double totalTime = 0.0;
    
    bool isValid() const {
        return !text.empty() && confidence > 0.0f;
    }
};

/**
 * Moteur OCR haute performance avec Tesseract natif
 */
class TesseractOCR {
public:
    struct Config {
        std::string language = "eng";
        tesseract::OcrEngineMode ocrMode = tesseract::OEM_LSTM_ONLY;
        tesseract::PageSegMode pageSegMode = tesseract::PSM_SINGLE_WORD;
        
        // Optimisations Tesseract
        std::unordered_map<std::string, std::string> tesseractVars = {
            {"tessedit_char_whitelist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,♠♥♦♣"},
            {"tessedit_do_invert", "0"},
            {"classify_enable_learning", "0"},
            {"classify_enable_adaptive_matcher", "1"},
            {"textord_really_old_xheight", "1"}
        };
        
        PreprocessConfig preprocessing;
        
        // Cache et performance
        bool enableCache = true;
        size_t maxCacheSize = 1000;
        
        // Threading
        bool enableParallel = true;
        int numThreads = 4;
        
        // Debugging
        bool saveDebugImages = false;
        std::string debugOutputPath = "./debug_ocr/";
    };

    explicit TesseractOCR(const Config& config = Config{});
    ~TesseractOCR();

    // Initialisation
    bool initialize();
    void shutdown();
    bool isInitialized() const { return initialized_; }

    // OCR principal
    OCRResult recognizeText(const cv::Mat& image, const cv::Rect& region = cv::Rect());
    std::vector<OCRResult> recognizeMultiple(const cv::Mat& image, const std::vector<cv::Rect>& regions);
    
    // OCR spécialisé poker
    std::string recognizeCard(const cv::Mat& cardImage);
    double recognizePot(const cv::Mat& potImage);
    double recognizeStack(const cv::Mat& stackImage);
    std::string recognizeAction(const cv::Mat& actionImage);
    
    // Préprocessing avancé
    cv::Mat preprocessImage(const cv::Mat& input);
    cv::Mat enhanceForCards(const cv::Mat& input);
    cv::Mat enhanceForNumbers(const cv::Mat& input);
    cv::Mat enhanceForText(const cv::Mat& input);

    // Configuration dynamique
    void updateConfig(const Config& newConfig);
    void setTesseractVariable(const std::string& key, const std::string& value);
    
    // Cache et optimisations
    void clearCache();
    void preloadCommonPatterns();
    
    // Statistiques et debugging
    struct Stats {
        uint64_t totalRecognitions = 0;
        double averageConfidence = 0.0;
        double averageTime = 0.0;
        uint64_t cacheHits = 0;
        uint64_t cacheMisses = 0;
        
        // Spécialisé poker
        uint64_t cardsRecognized = 0;
        uint64_t numbersRecognized = 0;
        uint64_t actionsRecognized = 0;
    };
    
    Stats getStatistics() const;
    void resetStatistics();
    
    // Calibration et tests
    bool testRecognition(const cv::Mat& testImage, const std::string& expectedText);
    double measureAccuracy(const std::vector<std::pair<cv::Mat, std::string>>& testData);

private:
    Config config_;
    std::unique_ptr<tesseract::TessBaseAPI> tesseract_;
    bool initialized_ = false;

    // Cache système
    struct CacheEntry {
        std::string text;
        float confidence;
        uint64_t timestamp;
        uint32_t accessCount;
    };
    
    mutable std::unordered_map<uint64_t, CacheEntry> ocrCache_;
    mutable std::mutex cacheMutex_;

    // Statistiques
    mutable std::mutex statsMutex_;
    Stats stats_;

    // Préprocessing pipeline
    cv::Mat applyGaussianBlur(const cv::Mat& image);
    cv::Mat applyBilateralFilter(const cv::Mat& image);
    cv::Mat applyAdaptiveThreshold(const cv::Mat& image);
    cv::Mat applyMorphology(const cv::Mat& image);
    cv::Mat applyResize(const cv::Mat& image);
    cv::Mat applyContrastEnhancement(const cv::Mat& image);
    cv::Mat applyDenoising(const cv::Mat& image);

    // Utilitaires internes
    uint64_t calculateImageHash(const cv::Mat& image, const cv::Rect& region);
    std::string cleanupRecognizedText(const std::string& rawText);
    float calculateConfidence(const std::string& text);
    
    // Optimisations spécialisées
    std::string recognizeCardRank(const cv::Mat& image);
    std::string recognizeCardSuit(const cv::Mat& image);
    double parseNumberString(const std::string& text);
    
    // Pattern matching
    bool matchesCardPattern(const std::string& text);
    bool matchesNumberPattern(const std::string& text);
    bool matchesActionPattern(const std::string& text);
    
    // Cache management
    void addToCache(uint64_t hash, const std::string& text, float confidence);
    bool getFromCache(uint64_t hash, std::string& text, float& confidence);
    void cleanupCache();

    // Debug et logging
    void saveDebugImage(const cv::Mat& image, const std::string& stage, const std::string& suffix = "");
    void logRecognitionResult(const OCRResult& result);
};

/**
 * Factory pour configurations prédéfinies
 */
class TesseractOCRFactory {
public:
    enum class PresetType {
        Fast,           // Performance maximale, précision réduite
        Accurate,       // Précision maximale, performance réduite
        Balanced,       // Équilibre performance/précision
        PokerOptimized, // Optimisé spécifiquement pour poker
        NumbersOnly,    // Optimisé reconnaissance de nombres
        CardsOnly       // Optimisé reconnaissance de cartes
    };

    static std::unique_ptr<TesseractOCR> create(PresetType type);
    static TesseractOCR::Config getPresetConfig(PresetType type);
};

} // namespace rtpa::ocr