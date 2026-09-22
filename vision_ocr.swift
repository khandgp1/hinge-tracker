import Foundation
import Vision
import AppKit

struct BoundingBox: Codable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double
    // Pixel coordinates (top-left origin)
    let pixelX: Int
    let pixelY: Int
    let pixelWidth: Int
    let pixelHeight: Int
}

struct TextObservation: Codable {
    let text: String
    let confidence: Float
    let box: BoundingBox
}

struct OCRResult: Codable {
    let imageWidth: Int
    let imageHeight: Int
    let observations: [TextObservation]
}

guard CommandLine.arguments.count > 1 else {
    let err = ["error": "Usage: vision_ocr <image_path>"]
    let data = try! JSONSerialization.data(withJSONObject: err)
    FileHandle.standardError.write(data)
    exit(1)
}

let imagePath = CommandLine.arguments[1]
let url = URL(fileURLWithPath: imagePath)

guard let image = NSImage(contentsOf: url),
      let tiffData = image.tiffRepresentation,
      let bitmapImage = NSBitmapImageRep(data: tiffData),
      let cgImage = bitmapImage.cgImage else {
    let err = ["error": "Failed to load CGImage from \(imagePath)"]
    let data = try! JSONSerialization.data(withJSONObject: err)
    FileHandle.standardError.write(data)
    exit(1)
}

let w = cgImage.width
let h = cgImage.height

var observationsList: [TextObservation] = []

let request = VNRecognizeTextRequest { (req, error) in
    guard let results = req.results as? [VNRecognizedTextObservation] else { return }
    for obs in results {
        if let candidate = obs.topCandidates(1).first {
            let normBox = obs.boundingBox
            // Convert from bottom-left normalized to top-left pixel
            let px = Int(round(normBox.origin.x * Double(w)))
            let py = Int(round((1.0 - normBox.origin.y - normBox.size.height) * Double(h)))
            let pw = Int(round(normBox.size.width * Double(w)))
            let ph = Int(round(normBox.size.height * Double(h)))
            
            let box = BoundingBox(
                x: normBox.origin.x,
                y: normBox.origin.y,
                width: normBox.size.width,
                height: normBox.size.height,
                pixelX: px,
                pixelY: py,
                pixelWidth: pw,
                pixelHeight: ph
            )
            observationsList.append(TextObservation(
                text: candidate.string,
                confidence: candidate.confidence,
                box: box
            ))
        }
    }
}

request.recognitionLevel = .accurate
request.usesLanguageCorrection = false

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
    let result = OCRResult(imageWidth: w, imageHeight: h, observations: observationsList)
    let encoder = JSONEncoder()
    encoder.outputFormatting = .prettyPrinted
    let jsonData = try encoder.encode(result)
    if let jsonString = String(data: jsonData, encoding: .utf8) {
        print(jsonString)
    }
} catch {
    let err = ["error": "Failed to run Vision request: \(error.localizedDescription)"]
    let data = try! JSONEncoder().encode(err)
    FileHandle.standardError.write(data)
    exit(1)
}
