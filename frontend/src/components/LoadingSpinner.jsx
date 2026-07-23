/**
 * LoadingSpinner — reusable animated spinner.
 * Props:
 *   size: "sm" | "md" | "lg"  (default: "md")
 *   color: tailwind text-color class  (default: "text-white")
 */
export default function LoadingSpinner({ size = 'md', color = 'text-white' }) {
  const sizeMap = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-10 h-10 border-3',
  }

  return (
    <div
      className={`
        ${sizeMap[size]} ${color}
        rounded-full border-current border-t-transparent animate-spin
      `}
      role="status"
      aria-label="Loading"
    />
  )
}
